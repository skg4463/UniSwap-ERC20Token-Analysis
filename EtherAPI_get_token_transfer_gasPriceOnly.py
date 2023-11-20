import requests
import time
import csv
from datetime import datetime
import pandas as pd

# Etherscan API 설정
API_KEY = 'SAWPUXJA5CHHQA9M5MD9Z2MVT31QHVCZHE'
BASE_URL = 'https://api.etherscan.io/api'
CONTRACT_ADDRESS = '0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640'

# CSV 파일 설정
AGGREGATED_CSV_FILE = 'aggregated_gas_prices1.csv'

# 타임스탬프를 일반 시간으로 변환하는 함수
def convert_timestamp(hex_timestamp):
    return datetime.utcfromtimestamp(int(hex_timestamp, 16)).strftime('%Y-%m-%d %H:%M:%S')

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
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print ("Oops: Something Else", err)

# 데이터를 1시간 단위로 리샘플링하는 함수
def resample_gas_prices(data, aggregated_file):
    df = pd.DataFrame(data, columns=['blockNumber', 'timeStamp', 'gasPrice'])
    df['timeStamp'] = pd.to_datetime(df['timeStamp'])
    df.set_index('timeStamp', inplace=True)

    # 시간대별로 그룹화하고 첫 번째 blockNumber와 timeStamp를 선택
    resampled_df = df.resample('H').agg({'blockNumber': 'first', 'gasPrice': 'mean'})

    # 인덱스를 리셋하고 timeStamp를 다시 열로 변환
    resampled_df.reset_index(inplace=True)
    resampled_df.to_csv(aggregated_file, index=False)

# 메인 로직
if __name__ == "__main__":
    start_block = '13948311'
    end_block = '16301003'
    page = 1
    offset = 1000
    all_data = []

    try:
        while True:
            logs = get_logs(start_block, end_block, page, offset)
            if logs and logs['result']:
                for log in logs['result']:
                    block_number = int(log['blockNumber'], 16)
                    timestamp = convert_timestamp(log['timeStamp'])
                    gas_price = int(log['gasPrice'], 16)
                    all_data.append([block_number, timestamp, gas_price])
                print(f"Page {page} data processed")
                page += 1
                time.sleep(0.3)
            else:
                print("No more data or error occurred.")
                break
        resample_gas_prices(all_data, AGGREGATED_CSV_FILE)
        print(f"Aggregated data saved to {AGGREGATED_CSV_FILE}")
    except Exception as e:
        print(f"An error occurred: {e}")
