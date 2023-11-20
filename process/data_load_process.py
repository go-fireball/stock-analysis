from data_loader.data_loader import DataLoader
import os.path

from strategy.slice_trader import SliceTrader

top_10 = [
    'AAPL',
    'MSFT',
    'AMZN',
    'NVDA',
    'META',
    'AVGO',
    'GOOG',
    'TSLA',
    'KLAC'
]

tickers = [
    'AAPL',
    'AMZN',
    'GOOG',
    'KLAC',
    'MSFT',
    'NVDA',
    'QCOM',
    'AVGO'
]
# data_loader = DataLoader()
# data_loader.load_tickers(top_10)

tickers_set1 = [
    'AAPL',
    'AMZN',
    'GOOG',
    'KLAC',
    'MSFT',
    'NVDA',
]
tickers_set2 = [
    'AAPL',
    'AMZN',
    'GOOG',
    'KLAC',
    'MSFT',
    'NVDA',
    'QCOM',
    'AVGO'
]
slice_trader = SliceTrader()
for ticker in tickers:
    data = slice_trader.calculate_strategy(tickers=top_10, daily_investment=100)

    strategy_name = 'top_10'
    target_file = 'data/temp/' + strategy_name + '_investment.xlsx'
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    data.to_excel(target_file, engine='openpyxl')
