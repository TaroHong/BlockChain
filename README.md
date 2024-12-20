# 📦 블록체인 기반 파일 저장 시스템
이 프로젝트는 **블록체인 기반 파일 저장 시스템**으로, Flask와 Geth, Web3.py를 사용하여 파일 업로드 및 블록체인에 데이터를 저장하는 기능을 제공합니다. 

이미지와 CSV 파일을 업로드하여 블럭을 생성한 후 블록체인에 저장합니다. 🚀
---

## 🌟 주요 기능
- **파일 업로드**: 이미지, CSV, 결과 파일 업로드 지원.
- **블록체인 저장**: 파일 데이터의 해시를 생성하고, 이를 블록체인에 저장.
- **제네시스 블록 자동 생성**: 블록체인 데이터가 없을 경우 제네시스 블록 자동 생성.
- **간단한 웹 인터페이스**: 블록 데이터와 파일 확인 가능.
- **스마트 계약 통합**: Ethereum 네트워크의 스마트 계약을 통해 블록 메타데이터 저장.
---

## 🛠️ 사용 기술
- **백엔드**: Flask, Web3.py
- **블록체인**: Geth (Ethereum 클라이언트)
- **파일 해싱**: SHA-256
- **데이터 저장소**: JSON 기반 로컬 저장 및 블록체인

---

## 🚀 설치 방법

### 사전 준비

1. **Python**: Python 3.7 이상 설치
2. **Geth**: Geth 설치 및 실행 (RPC 연결 확인 필수)
3. **Node.js** (선택): 프론트엔드 확장을 원하는 경우
4. **Solidity 컴파일러**: 스마트 계약 배포 및 편집 시 필요
5. **필수 라이브러리 설치**:
    🐍 Python
    🌍 Geth
    🌐 Web3

### 설정

1. **Geth 연결**  
   `app.py` 파일의 `infura_url` 값을 Geth RPC URL로 변경하세요.

2. **스마트 계약** 
   - ABI 파일(`abi.json`)을 `/root/ethblock/` 경로에 저장하세요.
   - 스마트 계약 주소를 `app.py`에 업데이트:

---

## 📝 사용법

### 서버 실행
0. Geth 실행합니다.
geth --http --http.addr "아이피" --http.port 5080 --http.corsdomain "*" --http.api "eth,web3,net"
geth account new -> 패스워드 입력
1. 
2. Flask 서버를 실행합니다.
python3 app.py

3. 브라우저에서 웹 인터페이스에 접속: 
 `http://<도메인>:포트`

4. REST API를 통해 파일 업로드: 

 **엔드포인트**: '/receive_파일'
 **메서드**: `POST` 
 **필수 파일**:
 - `csv_file`: 처리할 CSV 파일
 - `image_file`: 업로드할 이미지 파일
 - `result_file`: 결과 파일 (텍스트)


### 블록체인 데이터 확인

- **모든 블록 보기**: 
 'GET/블록'

- **특정 블록의 이미지 보기**: 
  `GET /blocks/<timestamp>/image_file.jpg`

---

## 🛡️ 스마트 계약 정보

스마트 계약은 Solidity로 작성되었으며, 블록 메타데이터 저장 기능을 제공합니다. 
주요 함수:
- `storeBlock(index, timestamp, inputDataHash, previousHash, result)`
- `getBlock(index)`

---

## 📂 프로젝트 구조

```
├── app.py # 플라스크 애플리케이션
├── /template # 플라스크 용 HTML 템플릿
├── /static # 정적 파일(CSS, JS 등)
├── /blocks # 블록 데이터 저장 경로
├── abi.json # 스마트 계약 ABI 파일
├── 블록체인_data.json # 로컬 블록체인 데이터 저장소
└── 계약.sol # 솔리드리티 스마트 계약 파일
```

/blocks 안에는 블록에 대한 정보들(index,timestamp,inputDataHash,previousHash)가 들어있으며 jpg와 csv에 대한 파일도 같이 있습니다. block의 이름은 타임스탬프로 저장합니다.

![image](https://github.com/user-attachments/assets/1dd84585-a02e-4484-a1b6-e8ca5251476f)


## 🔮 향후 개선 사항

- 파일 업로드에 대한 인증 및 암호화 추가.
- React, Vue.js와 같은 최신 UI 프레임워크로 프론트엔드 개선.
- IPFS를 통한 분산 파일 저장 지원.
- 스마트 계약에서 다중 서명 트랜잭션 지원.

---


## 📧 문의
-**이메일**: nos07054@naver.com ] 

## 📧 참고링크들
https://blog.naver.com/emmaeunji/221774107684
https://velog.io/@jhin/%EC%9E%90%EC%B2%B4-%EB%A9%94%EC%9D%B8%EB%84%B7-%EA%B5%AC%EC%B6%95
https://creal-news.tistory.com/category/%EB%B8%94%EB%A1%9D%EC%B2%B4%EC%9D%B8%20%EA%B3%B5%EB%B6%80
