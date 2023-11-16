import requests
import csv

# Etherscan API를 호출하기 위한 기본 설정
API_ENDPOINT = "https://api.etherscan.io/api"
API_KEY = "SAWPUXJA5CHHQA9M5MD9Z2MVT31QHVCZHE"  # 여기에 실제 API 키를 입력하세요.

# API 요청 매개변수 설정
params = {
    'module': 'account',
    'action': 'tokentx',
    'contractaddress': '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640',
    'page': 1,
    'offset': 100,
    'startblock': 16422226,
    'endblock': 16426657,
    'sort': 'asc',
    'apikey': API_KEY
}

# API 요청 및 응답 받기
response = requests.get(API_ENDPOINT, params=params)
data = response.json()

# 결과 확인
print(data)

# 응답 데이터를 CSV 파일로 저장
with open('token_transfers.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    # CSV 컬럼 헤더 작성
    writer.writerow(
        ["blockNumber", "timeStamp", "hash", "from", "contractAddress", "to", "value", "tokenName", "tokenSymbol",
         "tokenDecimal", "calculatedValue"])

    # 각 트랜잭션에 대한 정보를 CSV에 쓰기
    for tx in data['result']:
        # tokenDecimal을 적용하여 실제 값 계산
        calculated_value = int(tx['value']) / (10 ** int(tx['tokenDecimal']))
        writer.writerow([
            tx['blockNumber'],
            tx['timeStamp'],
            tx['hash'],
            tx['from'],
            tx['contractAddress'],
            tx['to'],
            tx['value'],
            tx['tokenName'],
            tx['tokenSymbol'],
            tx['tokenDecimal'],
            calculated_value
        ])
