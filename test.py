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
    print(data)
    if data and len(data) > days_ago:
        opening_price = data[-1]['opening_price']
        trade_price = data[0]['trade_price']
        change_rate = (trade_price - opening_price) / opening_price * 100
        # print(data)
        return change_rate
    return 0


def get_market_change_rates():
    """모든 원화 마켓 코인의 각 시간대별 등락률을 계산하는 함수"""
    url = "https://api.upbit.com/v1/market/all"
    markets = requests.get(url).json()
    krw_markets = [market['market'] for market in markets if market['market'].startswith('KRW')]

    market_change_rates = {}
    for market in krw_markets[:2]:
        rates = {
            '10min': round(get_change_rate(market, 'minutes/10', 2), 3),
            # '30min': round(get_change_rate(market, 'minutes/30'), 3),
            # '1hour': round(get_change_rate(market, 'minutes/60'), 3),
            # '1day': round(get_change_rate(market, 'days'), 3),
            # '2day': get_change_rate(market, 'days', 2),
            # '3day': get_change_rate(market, 'days', 3),
            # '4day': get_change_rate(market, 'days', 4),
            # '5day': get_change_rate(market, 'days', 5)
        }
        market_change_rates[market] = rates
        time.sleep(1)
        sys.stdout.write('.')
        sys.stdout.flush()

    return market_change_rates


def plot_data(type, markets, rates):
    # 그래프 생성
    plt.figure(figsize=(10, 6))
    plt.bar(markets, rates, color='blue')
    plt.xlabel('Market')
    plt.ylabel('Change Rate (%)')
    plt.xticks(rotation=90)  # x축 라벨 회전
    plt.title(type)
    plt.tight_layout()
    plt.show()
              

def anal_data(type, rates):
    print(type, rates)
    count = len([1 for item in rates if item < 0])
    print(f'{len(rates)}, {sum(rates)/len(rates):.1f}%, {count}, {count/len(rates)*100:.1f}%')
    

# 메인 함수 실행
if __name__ == "__main__":
    market_change_rates = get_market_change_rates()
    print("\n코인별 등락률:")
    
    markets = list(market_change_rates.keys())
    
    rates = [market_change_rates[market]['10min'] for market in markets]
    anal_data('10min', rates)
    plot_data('10min', markets, rates)
    
    # rates = [market_change_rates[market]['30min'] for market in markets]
    # anal_data('30min', rates)
    # plot_data('30min', markets, rates)
    
    # rates = [market_change_rates[market]['1hour'] for market in markets]
    # anal_data('1hour', rates)
    # plot_data('1hour', markets, rates)
    
    # rates = [market_change_rates[market]['1day'] for market in markets]
    # anal_data('1day', rates)
    # plot_data('1day',markets, rates)

    # for market, rates in market_change_rates.items():
    #     print(f"{market} - 10분: {rates['10min']:.2f}%, 1시간: {rates['1hour']:.2f}%, 1일: {rates['1day']:.2f}%")
