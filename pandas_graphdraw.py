import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np

# CSV 파일 읽기
df = pd.read_csv('uniswap_transactions.csv')

# 'timeStamp' 열을 datetime 객체로 변환
# 형식에 맞지 않는 경우 NaT로 설정
df['timeStamp'] = pd.to_datetime(df['timeStamp'], format='%Y-%m-%d %H:%M', errors='coerce')

# 변환에 실패한 데이터가 있는지 확인
if df['timeStamp'].isnull().any():
    print("There are some rows with incorrect date format:")
    print(df[df['timeStamp'].isnull()])


# 데이터 전처리: 'data' 열에서 뒤에서 두 번째 64바이트 데이터를 추출하여 10진수로 변환
def extract_liquidity(hex_data, blocknum):
    try:
        # 뒤에서 두 번째 64바이트 데이터 추출
        liquidity_hex = hex_data[-(2*64):-64]
        # 16진수를 10진수로 변환
        liquidity = int(liquidity_hex, 16)
        print(liquidity, blocknum)
        # 설정한 임계값보다 작은 값은 무시
        return np.log(liquidity) if liquidity < 1e20 else np.nan
    except (ValueError, TypeError):
        return np.nan


# 'Liquidity' 열 추가
# df['Liquidity'] = df['data'].apply(extract_liquidity)
df['Liquidity'] = df.apply(lambda row: extract_liquidity(row['data'], row['blockNumber']), axis=1)


# 인덱스를 'timeStamp'로 설정
df.set_index('timeStamp', inplace=True)

# 데이터 분석 및 그래프 그리기
# 예를 들어, 10분 간격으로 데이터를 리샘플링하여 트랜잭션 수를 카운트
transaction_counts = df.resample('10T').size()

# 트랜잭션 수를 막대 그래프로 표시
plt.figure(figsize=(15, 5))
transaction_counts.plot(kind='bar', color='skyblue')
plt.title('Number of Transactions Every 10 Minutes')
plt.xlabel('Time')
plt.ylabel('Number of Transactions')

plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

###################

# GasPrice와 GasUsed를 시간에 따라 그래프로 표시
fig, ax1 = plt.subplots(figsize=(15, 5))

# GasPrice를 선 그래프로 표시
color = 'tab:red'
ax1.set_xlabel('Time')
ax1.set_ylabel('Gas Price', color=color)
# ax1.plot(df.index, df['gasPrice'], color=color, label='GasPrice')
ax1.bar(df.index, df['gasPrice'], width=0.004, color=color, label='Gas Price')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_ylim([min(df['gasPrice']), max(df['gasPrice'])])  # Gas Price의 y축 범위 설정

# GasUsed를 막대 그래프로 표시
ax2 = ax1.twinx()  # 같은 x축을 공유하는 두 번째 y축 생성
color = 'tab:blue'
ax2.set_ylabel('Gas Used', color=color)
# ax2.bar(df.index, df['gasUsed'], width=0.0005, color=color, label='GasUsed', align='center')
ax2.bar(df.index, df['gasUsed'], width=0.0005, color=color, label='Gas Used', alpha=0.5)
ax2.tick_params(axis='y', labelcolor=color)
ax2.set_ylim([min(df['gasUsed']), max(df['gasUsed'])])  # Gas Used의 y축 범위 설정

# Liquidity를 꺾은선 그래프로 표시
ax3 = ax1.twinx()
ax3.spines['right'].set_position(('outward', 60))  # y축을 오른쪽으로 이동
color = 'tab:green'
ax3.set_ylabel('Liquidity', color=color)
ax3.plot(df.index, df['Liquidity'], color=color, linestyle='-', label='Liquidity')

ax3.tick_params(axis='y', labelcolor=color)

# 숫자 줄임 표현 비활성화
# ax1.yaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
# ax2.yaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
# ax3.yaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
# ax3.yaxis.get_major_formatter().set_scientific(False)  # ax3의 숫자 줄임 표현 비활성화

ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d\n%H:%M'))

# 제목과 레이아웃 조정
plt.title('Gas Price and Gas Used, and Liquidity Over Time')
# plt.legend(loc='upper left')
handles, labels = [], []
for ax in [ax1, ax2, ax3]:
    for h, l in zip(*ax.get_legend_handles_labels()):
        handles.append(h)
        labels.append(l)
ax1.legend(handles, labels, loc='upper left')

fig.tight_layout()
plt.show()
