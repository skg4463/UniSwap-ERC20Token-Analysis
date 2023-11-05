import pandas as pd
import matplotlib.pyplot as plt

# CSV 파일 읽기
df = pd.read_csv('uniswap_transactions.csv')

# 'timeStamp' 열을 datetime 객체로 변환
# 형식에 맞지 않는 경우 NaT로 설정
df['timeStamp'] = pd.to_datetime(df['timeStamp'], format='%Y-%m-%d %H:%M', errors='coerce')

# 변환에 실패한 데이터가 있는지 확인
if df['timeStamp'].isnull().any():
    print("There are some rows with incorrect date format:")
    print(df[df['timeStamp'].isnull()])

# 인덱스를 'timeStamp'로 설정
df.set_index('timeStamp', inplace=True)

# 이후에 데이터 분석 및 그래프 그리기 작업을 수행합니다.
# 예를 들어, 10분 간격으로 데이터를 리샘플링하여 트랜잭션 수를 카운트할 수 있습니다.
transaction_counts = df.resample('10T').size()

# 트랜잭션 수를 막대 그래프로 표시
plt.figure(figsize=(15, 5))
transaction_counts.plot(kind='bar', color='skyblue')
plt.title('Number of Transactions Every 10 Minutes')
plt.xlabel('Time')
plt.ylabel('Number of Transactions')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Gas Price와 Gas Used를 시간에 따라 그래프로 표시
fig, ax1 = plt.subplots(figsize=(15, 5))

# Gas Price를 선 그래프로 표시
color = 'tab:red'
ax1.set_xlabel('Time')
ax1.set_ylabel('Gas Price', color=color)
ax1.plot(df.index, df['gasPrice'], color=color)
ax1.tick_params(axis='y', labelcolor=color)

# Gas Used를 막대 그래프로 표시하기 위한 준비
ax2 = ax1.twinx()  # 같은 x축을 공유하는 두 번째 y축 생성
color = 'tab:blue'
ax2.set_ylabel('Gas Used', color=color)

# Gas Used를 막대 그래프로 표시
width = 0.0005  # 막대의 너비를 설정 (적절한 값으로 조정해야 할 수 있음)
ax2.bar(df.index, df['gasUsed'], width, color=color, label='Gas Used', align='center')
ax2.tick_params(axis='y', labelcolor=color)

# 제목과 레이아웃 조정
plt.title('Gas Price and Gas Used Over Time')
fig.tight_layout()
plt.show()