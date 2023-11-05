import requests
import csv
from time import sleep

# Etherscan API 키와 타겟 컨트랙트 주소를 설정합니다.
API_KEY = 'SAWPUXJA5CHHQA9M5MD9Z2MVT31QHVCZHE'
CONTRACT_ADDRESS = '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640'
OFFSET = 1000  # API 제한에 따라 조정 가능
URL = 'https://api.etherscan.io/api'

# Etherscan API를 사용하여 특정 컨트랙트 주소의 토큰 전송 내역을 가져오는 함수입니다.
def get_token_transfers(contract_address, start_block, end_block, page, offset, api_key):
    params = {
        'module': 'account',
        'action': 'tokentx',
        'contractaddress': contract_address,
        'startblock': start_block,
        'endblock': end_block,
        'page': page,
        'offset': offset,
        'sort': 'asc',
        'apikey': api_key
    }
    response = requests.get(URL, params=params)
    if response.status_code == 200:
        print(response.json())
        token_transfers = response.json()['result']
        # print(token_transfers)
        for tx in token_transfers:
            print(f"블록 {tx['blockNumber']}에서 트랜잭션 {tx['hash']} 수집됨")
        return token_transfers
    else:
        print('오류:', response.status_code)
        return None

# 모든 페이지를 순회하며 토큰 전송 내역을 수집합니다.
all_token_transfers = []
PAGE = 1
START_BLOCK = '12878196'  # 시작 블록 번호를 문자열로 설정합니다.
END_BLOCK = '12879196'  # 최신 블록까지 검색합니다.

while True:
    token_transfers = get_token_transfers(CONTRACT_ADDRESS, START_BLOCK, END_BLOCK, PAGE, OFFSET, API_KEY)
    if token_transfers:
        all_token_transfers.extend(token_transfers)
        PAGE += 1
        sleep(0.2)  # 초당 5개 요청을 고려하여 0.2초 대기합니다.
    else:
        # 더 이상 토큰 전송 내역이 없거나 마지막 페이지에 도달했을 경우 반복을 종료합니다.
        print('검색 종료')
        break

# 수집된 데이터를 CSV 파일로 저장합니다.
csv_columns = ['blockNumber', 'timeStamp', 'hash', 'from', 'to', 'value', 'contractAddress', 'tokenName', 'tokenSymbol', 'tokenDecimal', 'transactionIndex', 'gas', 'gasPrice', 'gasUsed', 'cumulativeGasUsed', 'input', 'confirmations']
csv_file = "token_transfers.csv"
try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for transfer in all_token_transfers:
            writer.writerow(transfer)
except IOError:
    print("I/O error")
