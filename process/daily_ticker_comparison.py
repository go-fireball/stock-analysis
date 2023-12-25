from process.data_loader import DataLoader
import os.path

from strategy.daily_trade_comparison import DailyTrader

slice_tickers = [
    'AAPL',
    'AMZN',
    'GOOG',
    'KLAC',
    'MSFT',
    'NVDA',

    'AVGO',
    'QCOM',
    'UBER',
    'TSLA',

    'QQQ',
    'TECL',
    'TQQQ',
    'SPY',

    'DXQLX',

]
data_loader = DataLoader()
data_loader.load_tickers(slice_tickers)

daily_trader = DailyTrader()
data = daily_trader.calculate_strategy(tickers=slice_tickers, daily_investment=100, start_date='1/1/2010')
strategy_name = 'selected_comparison'
target_file = 'data/temp/' + strategy_name + '_investment.xlsx'
os.makedirs(os.path.dirname(target_file), exist_ok=True)
data.to_excel(target_file, engine='openpyxl')
print('Process Completed')
