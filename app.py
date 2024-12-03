# -*- coding: utf-8 -*-
import os
import hashlib
import json
import shutil
import time
from time import time as current_time
from web3 import Web3
from flask import Flask, render_template, jsonify, request, send_from_directory

# Flask 애플리케이션 설정
app = Flask(__name__)

# 설정
BLOCKCHAIN_DIR = '/root/ethblock'
UPLOAD_FOLDER = os.path.join(BLOCKCHAIN_DIR, 'blocks')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 블록체인 데이터 저장소
blockchain_data = []

# 블록체인 데이터 파일 경로
blockchain_data_file = os.path.join(BLOCKCHAIN_DIR, 'blockchain_data.json')

# Geth 연결 설정
infura_url = 'geth 네트워크 실행한곳의 도메인'  # Geth의 RPC URL
w3 = Web3(Web3.HTTPProvider(infura_url))

# Geth에 연결되었는지 확인
if w3.is_connected:
    print("Geth에 연결되었습니다.")
    
    accounts = w3.eth.accounts
    if accounts:
        client_addresses = accounts  # 사용 가능한 모든 계정을 사용
        print(f"사용 가능한 계정: {client_addresses}")
    else:
        print("계정이 없습니다. 계정을 생성해 주세요.")
else:
    print("Geth에 연결할 수 없습니다.")

# 스마트 계약 주소와 ABI 설정
contract_address = '실제 배포된 계약 주소값'  
abi_file_path = 'abi 파일위치'

# ABI 파일 읽기
with open(abi_file_path, 'r') as abi_file:
    contract_abi = json.load(abi_file)

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def load_blockchain_data():
    """블록체인 데이터를 JSON 파일에서 로드합니다."""
    global blockchain_data
    if os.path.exists(blockchain_data_file):
        with open(blockchain_data_file, 'r') as f:
            blockchain_data = json.load(f)

def save_blockchain_data():
    """블록체인 데이터를 JSON 파일에 저장합니다."""
    with open(blockchain_data_file, 'w') as f:
        json.dump(blockchain_data, f, indent=4)

def create_genesis_block():
    """제네시스 블록을 생성합니다."""
    genesis_block = {
        'index': 1,
        'timestamp': int(current_time()),  # 타임스탬프를 정수로 변환
        'inputDataHash': '0',  # 제네시스 블록은 이전 해시가 없음
        'previousHash': '0',  # 이전 해시 없음
        'result': 'Genesis Block',
        'creationTime': 0.0  # 제네시스 블록의 생성 시간
    }
    blockchain_data.append(genesis_block)
    save_blockchain_data()  # 제네시스 블록을 파일에 저장
    print("제네시스 블록이 생성되었습니다.")

def generate_hash(file_path):
    """주어진 파일의 SHA-256 해시를 생성합니다."""
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def create_block_from_files(image_path, csv_path, result_path, client_address):
    """파일로부터 블록을 생성합니다."""
    start_time = current_time() * 1000  # 데이터 수신 시작 시간 기록 (밀리초)

    image_hash = generate_hash(image_path)
    csv_hash = generate_hash(csv_path)
    result_hash = generate_hash(result_path)

    # 모든 해시를 결합하여 하나의 문자열 생성
    combined_hash_string = "{}|{}|{}".format(image_hash, csv_hash, result_hash)

    # 결합된 해시 문자열에 대해 SHA-256 해시 생성
    input_data_hash = hashlib.sha256(combined_hash_string.encode()).hexdigest()

    previous_hash = blockchain_data[-1]['inputDataHash'] if blockchain_data else '0'

    # 블록 생성
    new_block = {
        'index': len(blockchain_data) + 1,
        'timestamp': int(current_time()),  # 타임스탬프를 정수로 변환
        'inputDataHash': input_data_hash,
        'previousHash': previous_hash,
        'result': open(result_path).read().strip(),  # 결과 파일 내용
        'creationTime': 0.0  # 초기화
    }

    # 블록 생성 후 현재 시간을 기록하여 creationTime 계산
    end_time = current_time() * 1000  # 블록 생성 완료 시간 기록 (밀리초)
    new_block['creationTime'] = round(end_time - start_time, 3)  # 데이터 수신부터 블록 생성까지 걸린 시간 (밀리초, 소수점 3자리)

    # 블록 데이터를 블록체인 데이터에 추가
    blockchain_data.append(new_block)

    # 블록체인 전체 정보 저장
    save_blockchain_data()

    # 타임스탬프를 폴더 이름으로 하는 블록 저장
    block_folder = os.path.join(UPLOAD_FOLDER, str(new_block['timestamp']))  # 정수로 변환된 타임스탬프 사용
    os.makedirs(block_folder, exist_ok=True)

    # JSON 파일로 블록 저장
    with open(os.path.join(block_folder, 'block.json'), 'w') as f:
        json.dump(new_block, f, indent=4)

    # 파일 저장
    shutil.copy(image_path, os.path.join(block_folder, 'image_file.jpg'))
    shutil.copy(csv_path, os.path.join(block_folder, 'csv_file.csv'))
    shutil.copy(result_path, os.path.join(block_folder, 'result_file.txt'))

    # Geth에 블록 데이터 저장
    gas_limit = 200000  # 고정된 가스 한도 설정

    tx_hash = contract.functions.storeBlock(
        int(new_block['index']),
        new_block['timestamp'],  # 정수로 변환된 타임스탬프 사용
        new_block['inputDataHash'],
        new_block['previousHash'],
        new_block['result']
    ).transact({
        'from': client_address,
        'gas': gas_limit  # 고정된 가스 한도를 사용
    })

    print("블록이 생성되었습니다: {}, 트랜잭션 해시: {}".format(new_block, tx_hash.hex()))

@app.route('/receive_files', methods=['POST'])
def receive_files():
    """CSV 및 이미지 파일을 수신합니다."""
    try:
        csv_file = request.files.get('csv_file')
        image_file = request.files.get('image_file')
        result_file = request.files.get('result_file')

        if not csv_file or not image_file or not result_file:
            return jsonify({'error': 'CSV, 이미지 또는 결과 파일이 누락되었습니다.'}), 400

        # 파일 저장 경로
        csv_path = os.path.join(UPLOAD_FOLDER, 'received_ocr_output.csv')
        image_path = os.path.join(UPLOAD_FOLDER, 'received_cropped_image.jpg')
        result_path = os.path.join(UPLOAD_FOLDER, 'received_result.txt')

        # 파일 저장
        csv_file.save(csv_path)
        image_file.save(image_path)
        result_file.save(result_path)

        # 블록 생성
        for client_address in client_addresses:
            create_block_from_files(image_path, csv_path, result_path, client_address)

        return jsonify({'message': '파일이 성공적으로 수신되었습니다.'}), 200

    except Exception as e:
        print(f"파일 수신 중 오류 발생: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template('index.html')

@app.route('/blocks')
def get_blocks():
    """블록체인 데이터를 JSON 형식으로 반환합니다."""
    return jsonify(blockchain_data)

@app.route('/blocks/<int:timestamp>/image_file.jpg')
def serve_image(timestamp):
    """타임스탬프에 해당하는 이미지 파일을 제공합니다."""
    block_folder = os.path.join(UPLOAD_FOLDER, str(timestamp))
    return send_from_directory(block_folder, 'image_file.jpg')

# 블록체인 데이터 로드
load_blockchain_data()

# 제네시스 블록이 없으면 생성
if not blockchain_data:
    create_genesis_block()

if __name__ == '__main__':
    app.run(host='서버아이피', port='원하는포트')
