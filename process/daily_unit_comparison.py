import os.path

from process.data_loader import DataLoader
from strategy.daily_trade_comparison import DailyUnitTrader

slice_tickers = [
    'AAPL',
    'AMZN',
    'GOOG',
    'KLAC',
    'MSFT',
    'NVDA',
    'AVGO',
    'QCOM',
    'TECL'

]
data_loader = DataLoader()
data_loader.load_tickers(slice_tickers)

daily_trader = DailyUnitTrader()
for ticker in slice_tickers:
    data = daily_trader.calculate_strategy(tickers=slice_tickers, daily_units=1, start_date='1/1/2015')

    strategy_name = 'selected_comparison_units'
    target_file = 'data/temp/' + strategy_name + '_investment.xlsx'
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    data.to_excel(target_file, engine='openpyxl')
