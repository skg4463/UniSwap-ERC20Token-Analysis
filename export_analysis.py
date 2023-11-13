import pandas as pd
import matplotlib.pyplot as plt

# 데이터 불러오기 및 초기 처리
file_path = 'export-address-token.csv'
data = pd.read_csv(file_path)

# 필요한 데이터 형태로 변환
data['DateTime (UTC)'] = pd.to_datetime(data['DateTime (UTC)'])
data['TokenValue'] = data['TokenValue'].replace({',': ''}, regex=True).astype(float)

# Uniswap 풀 주소
uniswap_pool_address = "0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640"


# 트랜잭션 유형 분류 함수 정의
def classify_transaction_pair(first, second):
    if first['Txhash'] != second['Txhash']:
        print(f"Exception: Mismatched transaction pair for Txhash: {first['Txhash']}")
        return 'Mismatched'  # Txhash가 다른 경우

    # Swap WETH for USDC
    if first['From'] == uniswap_pool_address and first['TokenSymbol'] == 'USDC' and \
            second['To'] == uniswap_pool_address and second['TokenSymbol'] == 'WETH':
        return 'Swap WETH for USDC'

    # Swap USDC for WETH
    elif first['From'] == uniswap_pool_address and first['TokenSymbol'] == 'WETH' and \
            second['To'] == uniswap_pool_address and second['TokenSymbol'] == 'USDC':
        return 'Swap USDC for WETH'

    # Add Liquidity
    elif first['To'] == uniswap_pool_address and second['To'] == uniswap_pool_address:
        return 'Add Liquidity'

    # Remove Liquidity
    elif first['From'] == uniswap_pool_address and second['From'] == uniswap_pool_address:
        return 'Remove Liquidity'

    print(f"Other transaction type identified for Txhash: {first['Txhash']}")
    return 'Other'


transaction_types = []
i = 0
while i < len(data):
    if i < len(data) - 1 and data.iloc[i]['Txhash'] == data.iloc[i + 1]['Txhash']:
        # 유효한 트랜잭션 쌍
        transaction_type = classify_transaction_pair(data.iloc[i], data.iloc[i + 1])
        transaction_types.extend([transaction_type, transaction_type])
        i += 2  # 다음 쌍으로 이동
    else:
        # 유효하지 않은 트랜잭션 쌍
        transaction_types.append('Mismatched')
        print(f"Exception: Mismatched transaction pair for Txhash: {data.iloc[i]['Txhash']}")
        i += 1  # 다음 트랜잭션으로 이동

# 마지막 트랜잭션 처리
if i == len(data) - 1:
    transaction_types.append('Incomplete')

# 데이터에 트랜잭션 유형 할당
data['TransactionType'] = transaction_types

# 예외 처리된 데이터 제거
data = data[data['TransactionType'] != 'Mismatched']
data = data[data['TransactionType'] != 'Incomplete']
data = data[data['TransactionType'] != 'Other']

# Swap action + Liquidity Action
# 유동성 관련 행위와 스왑 행위 분리
liquidity_actions = ['Add Liquidity', 'Remove Liquidity']
swap_actions = ['Swap WETH for USDC', 'Swap USDC for WETH']

# 리샘플링 및 그래프 생성
fig, ax = plt.subplots(figsize=(15, 8))

# 유동성 관련 행위
liquidity_data = data[data['TransactionType'].isin(liquidity_actions)]
liquidity_resampled = liquidity_data.resample('2H', on='DateTime (UTC)').sum()
ax.plot(liquidity_resampled.index, liquidity_resampled['TokenValue'], label='Liquidity Actions', color='blue')

# 스왑 행위
swap_data = data[data['TransactionType'].isin(swap_actions)]
swap_resampled = swap_data.resample('2H', on='DateTime (UTC)').sum()
ax.plot(swap_resampled.index, swap_resampled['TokenValue'], label='Swap Actions', color='green')

# Swap action + Liquidity Action (add, remove)
# # 수치형 데이터만 선택하고, 'TransactionType' 및 'DateTimeGroup' 열 추가
# numeric_data = data.select_dtypes(include=[np.number])
# numeric_data['TransactionType'] = data['TransactionType']
# numeric_data['DateTimeGroup'] = data['DateTime (UTC)'].dt.floor('1H')
#
# # 그룹화 및 합산
# grouped_data = numeric_data.groupby(['DateTimeGroup', 'TransactionType']).sum()
#
# # 토큰 이동량 요약
# token_movement_summary = grouped_data['TokenValue'].unstack(fill_value=0)
#
# # 그래프 생성
# fig, ax = plt.subplots(figsize=(15, 8))
# colors = ['blue', 'green', 'red']  # 각 유형별 색상 설정
# for (transaction_type, color) in zip(token_movement_summary.columns, colors):
#     ax.plot(token_movement_summary.index, token_movement_summary[transaction_type], \
#     label=transaction_type, color=color)

ax.set_xlabel('DateTime (2-hour intervals)')
ax.set_ylabel('Token Value Moved')
ax.legend(loc='upper left')
plt.title('Token Movement Over Time by Transaction Type')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
