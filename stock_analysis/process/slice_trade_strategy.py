import os.path
import json

from stock_analysis.dtos.slice import Slice
from stock_analysis.process.data_loader import DataLoader
from stock_analysis.strategy.slice_trader import SliceTrader

file_path = './stock_analysis/config/slices.json'
with open(file_path, 'r') as file:
    data = json.load(file)

slices = [Slice(item["name"], item["tickers"]) for item in data]

data_loader = DataLoader()

tickerSet = set([])
for individualSlice in slices:
    for ticker in individualSlice.tickers:
        tickerSet.add(ticker)

print(tickerSet)

data_loader.load_tickers(list(tickerSet))

slice_trader = SliceTrader()
for individualSlice in slices:
    data = slice_trader.calculate_strategy(tickers=individualSlice.tickers, daily_investment=100, start_date='1/1/2020'
                                           , rolling_window=200)
    target_file = 'data/temp/' + individualSlice.name + '_investment.xlsx'
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    data.to_excel(target_file, engine='openpyxl')
print('Process Completed')
