import requests
import datetime
import schedule
import time


# 업비트 API에서 지원하는 모든 시장 정보를 가져오는 함수
def get_all_markets():
    url = "https://api.upbit.com/v1/market/all"
    response = requests.get(url)
    markets = response.json()
    return [market['market'] for market in markets if market['market'].startswith('KRW')]  # 원화 마켓만 선택

# 업비트 API에서 시장 데이터를 가져오는 함수
def get_upbit_data(market):
    url = "https://api.upbit.com/v1/candles/minutes/1"  # 1분봉 데이터
    querystring = {"market":market,"count":"100"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    return data

# 데이터 분석 및 급증 지점 감지 함수
def detect_surge(market):
    data = get_upbit_data(market)
    surges = []
    for i in range(len(data)-1):
        current_deposit = data[i]['candle_acc_trade_price']
        previous_deposit = data[i+1]['candle_acc_trade_price']
        deposit_increase = (current_deposit - previous_deposit) / previous_deposit * 100

        current_price = data[i]['trade_price']
        previous_price = data[i+1]['trade_price']
        price_increase = (current_price - previous_price) / previous_price * 100

        if deposit_increase > 10 and price_increase > 5:
            surges.append(f"{market} 시간: {datetime.datetime.utcfromtimestamp(data[i]['timestamp']/1000)}, 입금액 증가율: {deposit_increase:.2f}%, 가격 증가율: {price_increase:.2f}%")
    return surges


def check_upbit_surge():
    # 급등을 체크하는 로직을 여기에 구현하세요.
    print("급등 체크 실행...")
    
    # 모든 코인에 대해 급증 지점 체크
    all_markets = get_all_markets()
    for market in all_markets:
        surges = detect_surge(market)
        if surges:
            print(f"{market}에 대한 급증 정보:")
            for surge in surges:
                print(surge)

# 30분마다 check_upbit_surge 함수를 실행합니다.
schedule.every(30).minutes.do(check_upbit_surge)

while True:
    # 스케줄된 작업을 실행합니다.
    schedule.run_pending()
    time.sleep(1)