import json
import os.path

from stock_analysis.process.data_loader import DataLoader
from stock_analysis.strategy.daily_trader import DailyTrader

file_path = './stock_analysis/config/tickers.json'
with open(file_path, 'r') as file:
    tickers = json.load(file)

data_loader = DataLoader()
data_loader.load_tickers(tickers)

daily_trader = DailyTrader()
data = daily_trader.calculate_strategy(tickers=tickers, daily_investment=100, start_date='1/1/2010')
target_file = 'data/temp/dollar_averaging.xlsx'
os.makedirs(os.path.dirname(target_file), exist_ok=True)
data.to_excel(target_file, engine='openpyxl')
print('Process Completed')
