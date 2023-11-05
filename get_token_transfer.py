import requests
import time
import csv
from datetime import datetime

# Etherscan API 설정
API_KEY = 'SAWPUXJA5CHHQA9M5MD9Z2MVT31QHVCZHE'
BASE_URL = 'https://api.etherscan.io/api'
CONTRACT_ADDRESS = '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640'

# CSV 파일 설정
CSV_FILE = 'uniswap_transactions2.csv'

# 타임스탬프를 일반 시간으로 변환하는 함수
def convert_timestamp(hex_timestamp):
    return datetime.utcfromtimestamp(int(hex_timestamp, 16)).strftime('%Y-%m-%d %H:%M:%S')

def format_address(address):
    return address[-40:]  # 뒤에서부터 40글자를 가져옴

def hex_to_int(hex_data):
    return int(hex_data, 16) if hex_data else 0

# 특정 블록 범위에 대한 로그를 가져오는 함수
def get_logs(start_block, end_block, page=1, offset=1000):
    params = {
        'module': 'logs',
        'action': 'getLogs',
        'fromBlock': start_block,
        'toBlock': end_block,
        'address': CONTRACT_ADDRESS,
        'page': page,
        'offset': offset,
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching logs: {response.status_code}")

# CSV 파일에 데이터를 저장하는 함수
def save_to_csv(data, filename):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        # CSV 헤더 작성
        writer.writerow(['blockNumber', 'timeStamp', 'transactionHash', 'sender', 'to', 'data', 'gasPrice', 'gasUsed'])
        # 데이터 작성 , 'data1', 'data2', 'data3'
        for log in data['result']:
            # from과 to 주소 추출 (topics[1]과 topics[2])
            from_address =format_address(log['topics'][1])
            to_address = format_address(log['topics'][2])
            value = int(log['data'], 16)
            writer.writerow([
                int(log['blockNumber'], 16),  # 16진수를 10진수로 변환
                convert_timestamp(log['timeStamp']),
                log['transactionHash'],
                from_address,
                to_address,
                log['data'],
                int(log['gasPrice'], 16),  # 16진수를 10진수로 변환
                int(log['gasUsed'], 16)  # 16진수를 10진수로 변환
            ])

# 메인 로직
if __name__ == "__main__":
    # 블록 범위 설정
    start_block = '16422226'
    end_block = '16426657'
    page = 1
    offset = 1000  # 한 페이지에 표시할 결과 수

    #try:
    #    logs = get_logs(start_block, end_block)
    #    save_to_csv(logs, CSV_FILE)
    #    print(f"Data saved to {CSV_FILE}")
    #except Exception as e:
    #    print(e)

    try:
        while True:
            logs = get_logs(start_block, end_block, page, offset)
            if logs['result']:
                save_to_csv(logs, CSV_FILE)
                page += 1  # 다음 페이지로 이동
                time.sleep(0.2)
            else:
                break  # 결과가 더 이상 없으면 반복을 종료
        print(f"Data saved to {CSV_FILE}")
    except Exception as e:
        print(e)

    # 요청 사이에 지연을 추가
    #time.sleep(0.2)  # 5회/초 제한에 맞추기 위해 0.2초 대기
