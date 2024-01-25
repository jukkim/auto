# functions.py

import requests
import json
import logging
from datetime import datetime
import requests
import jwt
import hashlib
import uuid
from urllib.parse import urlencode


# Initialize logging
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(config_file):
    with open(config_file, 'r') as file:
        return json.load(file)

def load_trade_data(trade_data_file):
    try:
        with open(trade_data_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_trade_data(trade_data_file, trade_data):
    with open(trade_data_file, 'w') as file:
        json.dump(trade_data, file, indent=4)

class TradeHistoryLogger:
    def __init__(self, log_file):
        self.log_file = log_file
        
    def log_trade(self, trade_type, coin, quantity):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as file:
            file.write(f"{timestamp} {trade_type} {coin} {quantity:.8f}\n")

# PseudoTradingAPI.py

class PseudoTradingAPI:
    def __init__(self, access_key, secret_key, base_url='https://api.upbit.com'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url

    def get_current_price(self, ticker):
        """가짜 시장 가격 조회 함수. 실제 환경에서는 거래소의 실시간 가격을 조회하는 API 요청을 구현해야 한다."""
        url = f"{self.base_url}/v1/ticker?markets={ticker}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # 오류가 있을 경우 예외를 발생시킨다.
            data = response.json()
            if data:
                # 마켓 코드에 따라 첫 번째 아이템의 현재 가격을 반환한다.
                return data[0]['trade_price']
            else:
                return None  # 조회된 데이터가 없는 경우
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current price data: {str(e)}")
            return None

    # 다른 거래 관련 메소드 (buy, sell 등) 또한 여기에 구현해야 할 것이다.
    def buy(self, coin, quantity):
        pass # Implement actual buy logic with API call
    
    def sell(self, coin, quantity):
        pass # Implement actual sell logic with API call



class UpbitTradingAPI:
    def __init__(self, access_key, secret_key, server_url='https://api.upbit.com'):
        self.access_key = access_key
        self.secret_key = secret_key
        self.server_url = server_url

    def get_current_price(self, market):
        # 업비트의 경우 배치 요청으로 한 번에 여러 마켓의 가격을 가져올 수 있음
        url = self.server_url + "/v1/ticker"
        try:
            response = requests.get(url, params={'markets': market})
            response.raise_for_status()  # 문제 발생 시 예외 발생
            return response.json()[0]['trade_price']
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Exception as err:
            print(f"An error occurred: {err}")

    def buy(self, market, price):
        # 지정가 주문의 경우 price를 설정
        return self._order(market, 'bid', price, None)

    def sell(self, market, volume):
        # 시장가 매도 주문의 경우 volume을 설정
        return self._order(market, 'ask', None, volume)

    def _order(self, market, side, price, volume):
        # 업비트 주문 요청은 항상 POST 메서드를 사용하고, 주문 정보는 JWT 토큰에 인코딩됨
        # 파라미터로 오는 가격과 수량 중 하나를 설정
        query = {
            'market': market,
            'side': side,  # 매수는 'bid' 매도는 'ask'
            'price': str(price) if price else None,
            'volume': str(volume) if volume else None,
            'ord_type': 'price' if price else 'market',  # 지정가 혹은 시장가 주문
        }
        query_string = urlencode(query).encode()
        m = hashlib.sha512()
        m.update(query_string)
        query_hash = m.hexdigest()

        payload = {
            'access_key': self.access_key,
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512',
        }

        jwt_token = jwt.encode(payload, self.secret_key).decode('utf8')
        headers = {"Authorization": f"Bearer {jwt_token}"}

        response = requests.post(self.server_url + "/v1/orders", params=query, headers=headers)
        return response.json()  # 주문 결과 반환



class CoinTrader:
    def __init__(self, coin, config):
        self.coin = coin
        self.trade_amount = config['trade_amount']
        self.trade_counts = config['trade_counts'][coin]
        self.purchases = []  # This will be loaded from file
        self.highest_value_since_last_purchase = 0

    def record_purchase(self, price, quantity, timestamp):
        # Record a new purchase
        self.purchases.append({
            'amount': price,
            'quantity': quantity,
            'timestamp': timestamp,
            'sold': False
        })

    def record_sell(self, price, quantity, timestamp):
        # Update a purchase as sold
        for purchase in self.purchases:
            if not purchase['sold']:
                purchase['sold'] = True
                purchase['sell_price'] = price
                purchase['sell_quantity'] = quantity
                purchase['sell_timestamp'] = timestamp
                break

    def update_highest_value(self, current_price):
        self.highest_value_since_last_purchase = max(self.highest_value_since_last_purchase, current_price)

    def get_lowest_unsold_purchase_amount(self):
        unsold_purchases = [p for p in self.purchases if not p['sold']]
        return min(unsold_purchases, key=lambda x: x['amount'])['amount'] if unsold_purchases else None
        
    def should_buy(self, current_price):
        lowest_purchase_amount = self.get_lowest_unsold_purchase_amount()
        price_drop = lowest_purchase_amount is not None and current_price < lowest_purchase_amount * 0.995
        price_below_highest = current_price < self.highest_value_since_last_purchase * 0.995
        return price_drop and price_below_highest or (lowest_purchase_amount is None and price_below_highest)

    def should_sell(self, current_price):
        lowest_purchase_amount = self.get_lowest_unsold_purchase_amount()
        return lowest_purchase_amount is not None and current_price > lowest_purchase_amount * 1.005
