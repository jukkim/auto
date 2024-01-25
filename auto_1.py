# Upbit 트레이딩 봇의 메인 부분과 함수 부분을 분리하여 파일로 저장합니다.

# 함수 부분
upbit_trading_bot_functions_code = """
import pyupbit
import json
import os
from datetime import datetime

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def load_purchase_records(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_purchase_records(filename, records):
    with open(filename, 'w') as file:
        json.dump(records, file)

def log_trade(filename, record):
    with open(filename, 'a') as file:
        file.write(json.dumps(record) + '\\n')

def get_next_purchase_id(records):
    if records:
        return max(records.keys(), default=0) + 1
    return 1

def complete_trade(record_id, current_price, purchase_records, trade_time_format):
    purchase_records[record_id]['completed'] = True
    purchase_records[record_id]['sell_price'] = current_price
    purchase_records[record_id]['sell_time'] = datetime.now().strftime(trade_time_format)
    print(f"Trade {record_id} completed at price {purchase_records[record_id]['sell_price']}")

def place_order(upbit, symbol, side, quantity, current_price, purchase_records, trade_time_format, trade_log_filename):
    try:
        print(f"Placing a {side} order for {quantity} of {symbol} at {current_price}")

        if side == 'BUY':
            order = upbit.buy_market_order(symbol, quantity * current_price)
            purchase_id = get_next_purchase_id(purchase_records)
            new_record = {
                'quantity': quantity, 
                'price': current_price, 
                'completed': False, 
                'type': 'BUY',
                'buy_time': datetime.now().strftime(trade_time_format)
            }
            purchase_records[purchase_id] = new_record
            print(f"Purchase record added: {purchase_records[purchase_id]}")
            save_purchase_records(purchase_records_filename, purchase_records)
            log_trade(trade_log_filename, new_record)
    except Exception as e:
        print(f"An error occurred - {e}")

def check_for_sale_opportunities(current_price, purchase_records, trade_log_filename, trade_time_format):
    lowest_purchase_id = None
    lowest_purchase_price = float('inf')

    for record_id, record in purchase_records.items():
        if not record['completed'] and record['price'] < lowest_purchase_price:
            lowest_purchase_price = record['price']
            lowest_purchase_id = record_id

    if lowest_purchase_id and current_price >= 1.01 * lowest_purchase_price:
        complete_trade(lowest_purchase_id, current_price, purchase_records, trade_time_format)
        save_purchase_records(purchase_records_filename, purchase_records)

def calculate_quantity_from_amount(current_price, amount):
    return amount / current_price

def get_last_purchase_price(purchase_records):
    if purchase_records:
        return max(record['price'] for record_id, record in purchase_records.items() if not record['completed'])
    return None

def count_open_trades(purchase_records):
    return sum(1 for record in purchase_records.values() if not record['completed'])
"""

# 메인 부분
upbit_trading_bot_main_code = """
# Upbit 접속
access = "YOUR_ACCESS_KEY"
secret = "YOUR_SECRET_KEY"
upbit = pyupbit.Upbit(access, secret)

symbol = "KRW-BTC"
initial_price = pyupbit.get_current_price(symbol)
print(f"Initial Price: {initial_price}")

config_filename = 'config.json'
config = load_config(config_filename)

min_drop_percentage_to_buy = config['min_drop_percentage_to_buy']
max_drop_percentage_to_buy = config['max_drop_percentage_to_buy']
threshold_for_extra_drop = config['threshold_for_extra_drop']
max_open_trades = config['max_open_trades']
loop_restart_time = config['loop_restart_time']
trade_time_format = config['trade_time_format']
trade_amount = config['trade_amount']

purchase_records_filename = 'purchase_records.json'
purchase_records = load_purchase_records(purchase_records_filename)
trade_log_filename = 'trade_log.txt'  # 거래 기록 파일

def load_config(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def load_purchase_records(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        return {}

def save_purchase_records(filename, records):
    with open(filename, 'w') as file:
        json.dump(records, file)

def log_trade(filename, record):
    with open(filename, 'a') as file:
        file.write(json.dumps(record) + '\\n')

def get_next_purchase_id(records):
    if records:
        return max(records.keys(), default=0) + 1
    return 1

def complete_trade(record_id, current_price, purchase_records, trade_time_format):
    purchase_records[record_id]['completed'] = True
    purchase_records[record_id]['sell_price'] = current_price
    purchase_records[record_id]['sell_time'] = datetime.now().strftime(trade_time_format)
    print(f"Trade {record_id} completed at price {purchase_records[record_id]['sell_price']}")

def place_order(upbit, symbol, side, quantity, current_price, purchase_records, trade_time_format, trade_log_filename):
    try:
        print(f"Placing a {side} order for {quantity} of {symbol} at {current_price}")

        if side == 'BUY':
            order = upbit.buy_market_order(symbol, quantity * current_price)
            purchase_id = get_next_purchase_id(purchase_records)
            new_record = {
                'quantity': quantity, 
                'price': current_price, 
                'completed': False, 
                'type': 'BUY',
                'buy_time': datetime.now().strftime(trade_time_format)
            }
            purchase_records[purchase_id] = new_record
            print(f"Purchase record added: {purchase_records[purchase_id]}")
            save_purchase_records(purchase_records_filename, purchase_records)
            log_trade(trade_log_filename, new_record)
    except Exception as e:
        print(f"An error occurred - {e}")

def check_for_sale_opportunities(current_price, purchase_records, trade_log_filename, trade_time_format):
    lowest_purchase_id = None
    lowest_purchase_price = float('inf')

    for record_id, record in purchase_records.items():
        if not record['completed'] and record['price'] < lowest_purchase_price:
            lowest_purchase_price = record['price']
            lowest_purchase_id = record_id

    if lowest_purchase_id and current_price >= 1.01 * lowest_purchase_price:
        complete_trade(lowest_purchase_id, current_price, purchase_records, trade_time_format)
        save_purchase_records(purchase_records_filename, purchase_records)

def calculate_quantity_from_amount(current_price, amount):
    return amount / current_price

def get_last_purchase_price(purchase_records):
    if purchase_records:
        return max(record['price'] for record_id, record in purchase_records.items() if not record['completed'])
    return None

def count_open_trades(purchase_records):
    return sum(1 for record in purchase_records.values() if not record['completed'])


while True:
    time.sleep(loop_restart_time)
    current_price = pyupbit.get_current_price(symbol)
    last_purchase_price = get_last_purchase_price(purchase_records)

    check_for_sale_opportunities(current_price, purchase_records, trade_log_filename, trade_time_format)

    if count_open_trades(purchase_records) < max_open_trades:
        drop_percentage_to_buy = min_drop_percentage_to_buy
        if current_price < initial_price:
            drop_from_initial = 
