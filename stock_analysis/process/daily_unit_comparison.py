import os.path
import json

from stock_analysis.process.data_loader import DataLoader
from stock_analysis.strategy.daily_unit_trader import DailyUnitTrader

file_path = './stock_analysis/config/tickers.json'
with open(file_path, 'r') as file:
    tickers = json.load(file)

data_loader = DataLoader()
data_loader.load_tickers(tickers)

daily_trader = DailyUnitTrader()
data = daily_trader.calculate_strategy(tickers=tickers, daily_units=1, start_date='1/1/2015')
strategy_name = 'selected_comparison_units'
target_file = 'data/temp/' + strategy_name + '_investment.xlsx'
os.makedirs(os.path.dirname(target_file), exist_ok=True)
data.to_excel(target_file, engine='openpyxl')
