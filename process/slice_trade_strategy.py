from data_loader.data_loader import DataLoader
import os.path

from strategy.slice_trader import SliceTrader

slice_tickers = [
    'AAPL',
    'AMZN',
    'GOOG',
    'KLAC',
    'MSFT',
    'AVGO'
]
data_loader = DataLoader()
data_loader.load_tickers(slice_tickers)

slice_trader = SliceTrader()
for ticker in slice_tickers:
    data = slice_trader.calculate_strategy(tickers=slice_tickers, daily_investment=100)

    strategy_name = 'selected_six'
    target_file = 'data/temp/' + strategy_name + '_investment.xlsx'
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    data.to_excel(target_file, engine='openpyxl')
