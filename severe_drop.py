import requests
import time
import sys
import matplotlib.pyplot as plt


def get_change_rate(market, interval, days_ago=0):
    """주어진 시간 간격에 대한 코인의 등락률을 계산하는 함수"""
    url = f"https://api.upbit.com/v1/candles/{interval}"
    params = {'market': market, 'count': days_ago + 1}
    response = requests.get(url, params=params)
    data = response.json()
    rates = []
    
    if data and len(data) > days_ago:
        for idx, item in enumerate(data) :
            if item:
                # print(idx, item)
                opening_price = data[idx]['opening_price']
                trade_price = data[idx]['trade_price']
                change_rate = (trade_price - opening_price) / opening_price * 100
                rates.append(change_rate)
        
        # print(rates)
        return rates

    return []


def get_market_change_rates(num):
    """모든 원화 마켓 코인의 각 시간대별 등락률을 계산하는 함수"""
    url = "https://api.upbit.com/v1/market/all"
    markets = requests.get(url).json()
    krw_markets = [market['market'] for market in markets if market['market'].startswith('KRW')]

    market_change_rates = {}
    for market in krw_markets:
        rates = get_change_rate(market, 'minutes/10', num)
        market_change_rates[market] = rates
        time.sleep(0.1)
        sys.stdout.write('.')
        sys.stdout.flush()

    return market_change_rates


def anal_data(type, rates):
    # print(type, rates)
    count = len([1 for item in rates if item < 0])
    print(f'{type}th => {len(rates)}, {sum(rates)/len(rates):.2f}%, {count}, {count/len(rates)*100:.1f}%')
    

# 메인 함수 실행
if __name__ == "__main__":
    num = 5
    market_change_rates = get_market_change_rates(num)
    print("\n코인별 등락률:")
    # print(market_change_rates)   
    markets = list(market_change_rates.keys())   
    
    for i in range(num+1):
        rates = [market_change_rates[market][i] for market in markets]
        # print(rates)
        anal_data(i, rates)
