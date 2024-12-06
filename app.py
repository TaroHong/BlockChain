# -*- coding: utf-8 -*-
import os
import hashlib
import json
import shutil
import re
from time import time as current_time
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from web3 import Web3
from flask import Flask, jsonify, render_template
from flask_cors import CORS

# Flask 설정
app = Flask(__name__, template_folder='/home/nos07054/outethblock/templates')
CORS(app, resources={r"/*": {"origins": "*"}})

# 경로 설정
BLOCKCHAIN_DIR = '/home/nos07054/outethblock'
UPLOAD_FOLDER = os.path.join(BLOCKCHAIN_DIR, 'blocks')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

IMAGE_DIR = '/home/nos07054/outethblock/images'
CSV_DIR = '/home/nos07054/outethblock/csv_files'

# 처리된 파일 기록용 저장소
processed_files_file = os.path.join(BLOCKCHAIN_DIR, 'processed_files.json')
processed_files = set()

# Geth 설정
infura_url = 'geth 네트워크 아이피'
w3 = Web3(Web3.HTTPProvider(infura_url))

blockchain_data = []
blockchain_data_file = os.path.join(BLOCKCHAIN_DIR, 'blockchain_data.json')

contract_address = '컨트렉트 주소값'
abi_file_path = '솔리디티로 만든 abi 데이터'

# ABI 로드
try:
    with open(abi_file_path, 'r') as abi_file:
        contract_abi = json.load(abi_file)
except FileNotFoundError:
    print("[ERROR] ABI 파일을 찾을 수 없습니다. 경로를 확인하세요.")
    exit()

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

if w3.is_connected():
    print("[LOG] Geth에 연결되었습니다.")
    accounts = w3.eth.accounts
    if accounts:
        client_addresses = accounts
        print(f"[LOG] 사용 가능한 계정: {client_addresses}")
    else:
        print("[WARNING] 계정이 없습니다. 계정을 생성하거나 가져오세요.")
else:
    print("[ERROR] Geth에 연결할 수 없습니다. Geth 노드 상태를 확인하세요.")
    exit()

# 블록체인 데이터 로드 및 저장
def load_blockchain_data():
    global blockchain_data, processed_files
    if os.path.exists(blockchain_data_file):
        with open(blockchain_data_file, 'r') as f:
            blockchain_data = json.load(f)
        print(f"[DEBUG] 로드된 블록 데이터 개수: {len(blockchain_data)}개")
    else:
        print("[WARNING] 블록체인 데이터 파일이 존재하지 않습니다.")

    if os.path.exists(processed_files_file):
        with open(processed_files_file, 'r') as f:
            processed_files = set(json.load(f))
        print(f"[DEBUG] 로드된 처리된 파일 목록 개수: {len(processed_files)}개")
    else:
        print("[WARNING] 처리된 파일 목록이 존재하지 않습니다.")

def save_blockchain_data():
    try:
        with open(blockchain_data_file, 'w') as f:
            json.dump(blockchain_data, f, indent=4)
        print("[LOG] 블록체인 데이터 저장 완료.")
    except Exception as e:
        print(f"[ERROR] 블록체인 데이터 저장 중 오류 발생: {str(e)}")

def save_processed_files():
    try:
        sorted_processed_files = sorted(
            processed_files,
            key=lambda x: int(re.search(r'\d+', x).group())
        )
        with open(processed_files_file, 'w') as f:
            json.dump(sorted_processed_files, f, indent=4)
        print("[LOG] 처리된 파일 목록 저장 완료 (정렬됨).")
    except Exception as e:
        print(f"[ERROR] 처리된 파일 목록 저장 중 오류 발생: {str(e)}")

# 제네시스 블록 생성
def create_genesis_block():
    if not blockchain_data:
        genesis_block = {
            'index': 1,
            'timestamp': int(current_time()),
            'inputDataHash': '0',
            'previousHash': '0',
            'creationTime': 0.0
        }
        blockchain_data.append(genesis_block)
        save_blockchain_data()
        print("[LOG] 제네시스 블록이 생성되었습니다.")

# 해시 생성
def generate_hash(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        print(f"[ERROR] 파일 해시 생성 중 오류 발생: {str(e)}")
        return None

def create_block(image_path, csv_path, client_address):
    try:
        file_key = f"{os.path.basename(image_path)}|{os.path.basename(csv_path)}"
        if file_key in processed_files:
            print(f"[SKIP] 이미 처리된 파일: {file_key}")
            return

        start_time = current_time() * 1000
        image_hash = generate_hash(image_path)
        csv_hash = generate_hash(csv_path)

        combined_hash_string = f"{image_hash}|{csv_hash}"
        input_data_hash = hashlib.sha256(combined_hash_string.encode()).hexdigest()
        previous_hash = blockchain_data[-1]['inputDataHash'] if blockchain_data else '0'

        new_block = {
            'index': len(blockchain_data) + 1,
            'timestamp': int(current_time()),
            'inputDataHash': input_data_hash,
            'previousHash': previous_hash,
            'creationTime': 0.0
        }

        end_time = current_time() * 1000
        new_block['creationTime'] = round(end_time - start_time, 3)
        blockchain_data.append(new_block)
        save_blockchain_data()

        # 폴더 이름 생성 (중복 방지)
        timestamp = str(new_block['timestamp'])
        block_folder = os.path.join(UPLOAD_FOLDER, timestamp)
        suffix = 1

        while os.path.exists(block_folder):  # 중복된 폴더가 있으면 suffix 추가
            block_folder = os.path.join(UPLOAD_FOLDER, f"{timestamp}-{suffix}")
            suffix += 1

        os.makedirs(block_folder, exist_ok=True)

        with open(os.path.join(block_folder, 'block.json'), 'w') as f:
            json.dump(new_block, f, indent=4)
        shutil.copy(image_path, os.path.join(block_folder, 'image_file.jpg'))
        shutil.copy(csv_path, os.path.join(block_folder, 'csv_file.csv'))

        processed_files.add(file_key)
        save_processed_files()

        print(f"[LOG] 블록 생성 완료: {new_block}")
    except Exception as e:
        print(f"[ERROR] 블록 생성 중 오류 발생: {str(e)}")

# 파일 변경 감지 핸들러
class FileChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        prefix = os.path.splitext(os.path.basename(file_path))[0].split('_')[0]

        image_path = os.path.join(IMAGE_DIR, f"{prefix}_cropped_uv.jpg")
        csv_path = os.path.join(CSV_DIR, f"{prefix}_metadata.csv")

        if os.path.exists(image_path) and os.path.exists(csv_path):
            print(f"[DEBUG] 파일 변경 감지: {image_path}, {csv_path}")
            for client_address in client_addresses:
                create_block(image_path, csv_path, client_address)

# 초기 파일 처리
def process_existing_files():
    print("[LOG] 초기 파일 처리 시작...")
    
    # 이미지 파일과 CSV 파일 정렬
    image_files = sorted([f for f in os.listdir(IMAGE_DIR) if f.endswith('_cropped_uv.jpg')])
    csv_files = sorted([f for f in os.listdir(CSV_DIR) if f.endswith('_metadata.csv')])
    
    print(f"[LOG] 발견된 이미지 파일 개수: {len(image_files)}")
    print(f"[LOG] 발견된 CSV 파일 개수: {len(csv_files)}")
    
    # 매칭된 파일 리스트 생성
    matched_files = []
    
    for image_file in image_files:
        image_prefix = os.path.splitext(image_file)[0].split('_')[0]  # 이미지 파일의 접두사 추출
        csv_file = f"{image_prefix}_metadata.csv"  # 매칭될 CSV 파일 이름 생성
        csv_path = os.path.join(CSV_DIR, csv_file)
        
        if os.path.exists(csv_path):
            matched_files.append((image_file, csv_file))  # 매칭된 파일 저장

    print(f"[LOG] 매칭된 파일 개수: {len(matched_files)}")
    
    # 매칭된 파일 순서대로 블록 생성
    matched_files.sort(key=lambda x: int(re.search(r'\d+', x[0]).group()))  # 숫자 순 정렬
    
    for image_file, csv_file in matched_files:
        image_path = os.path.join(IMAGE_DIR, image_file)
        csv_path = os.path.join(CSV_DIR, csv_file)
        file_key = f"{image_file}|{csv_file}"

        if file_key in processed_files:
            print(f"[SKIP] 이미 처리된 파일: {file_key}")
            continue

        print(f"[DEBUG] 블록 생성 시작: {image_path}, {csv_path}")
        for client_address in client_addresses:
            create_block(image_path, csv_path, client_address)

        processed_files.add(file_key)

    # 저장 처리
    save_processed_files()
    print(f"[LOG] 초기 파일 처리 완료. 총 처리된 파일 개수: {len(processed_files)}")

# Flask 엔드포인트
@app.route('/')
def index():
    return render_template('monitor.html')

@app.route('/blocks')
def get_blocks():
    return jsonify(blockchain_data)

# 메인
if __name__ == '__main__':
    load_blockchain_data()
    process_existing_files()
    create_genesis_block()

    observer = Observer()
    observer.schedule(FileChangeHandler(), path=IMAGE_DIR, recursive=False)
    observer.schedule(FileChangeHandler(), path=CSV_DIR, recursive=False)
    Thread(target=observer.start).start()

    app.run(host='0.0.0.0', port=5080, debug=True)
