# main.py

from functions import load_config, load_trade_data, save_trade_data, TradeHistoryLogger, PseudoTradingAPI, UpbitTradingAPI, CoinTrader
import time, datetime

def main():
    config = load_config('config.json')
    trade_data = load_trade_data('trade_data.json')
    
    trade_logger = TradeHistoryLogger('trade_history.log')
    # trading_api = UpbitTradingAPI()
    trading_api = PseudoTradingAPI()
    traders = {coin: CoinTrader(coin, config) for coin in config['coins']}
    
    while True:
        try:
            for coin, trader in traders.items():
                current_price = trading_api.get_current_price(coin)  # Replace with actual price fetching
                
                if trader.should_buy(current_price):
                    quantity = trader.trade_amount / current_price
                    trading_api.buy(coin, quantity)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trader.record_purchase(current_price, quantity, timestamp)
                    trade_logger.log_trade("BUY", coin, quantity)

                elif trader.should_sell(current_price):
                    quantity = trader.trade_amount / current_price
                    trading_api.sell(coin, quantity)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    trader.record_sell(current_price, quantity, timestamp)
                    trade_logger.log_trade("SELL", coin, quantity)

            save_trade_data('trade_data.json', {coin: trader.purchases for coin, trader in traders.items()})
            time.sleep(config['sleep_time'])
            
        except KeyboardInterrupt:
            # Clean up and save before exiting
            save_trade_data('trade_data.json', {coin: trader.purchases for coin, trader in traders.items()})
            print("Program exited cleanly")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

# 업비트 API 인증을 위해 발급받은 access_key와 secret_key를 사용해야 한다.
# trading_api = UpbitTradingAPI('YOUR_ACCESS_KEY', 'YOUR_SECRET_KEY')
# current_price = trading_api.get_current_price("KRW-BTC")
# buy_order = trading_api.buy("KRW-BTC", 50000)
# sell_order = trading_api.sell("KRW-BTC", 0.001)