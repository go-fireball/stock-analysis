import os.path

from process.data_loader import DataLoader
from strategy.slice_trader import SliceTrader

slices = {
    'six': [
        'AAPL',
        'AMZN',
        'GOOG',
        'KLAC',
        'MSFT',
        'NVDA'
    ],
    'ai-slice': [
        'AAPL',
        'AMZN',
        'GOOG',
        'KLAC',
        'MSFT',
        'NVDA',
        'AVGO',
        'QCOM'
    ],
    'diversified': [
        'AAPL',
        'AMZN',
        'GOOG',
        'KLAC',
        'MSFT',
        'NVDA',
        'UBER',
        'AVGO',
        'TSLA',
        'META'
    ],
    'sp500': [
        '^GSPC'
    ]
}

data_loader = DataLoader()

tickerSet = set([])
for key, value in slices.items():
    for ticker in value:
        tickerSet.add(ticker)

print(tickerSet)

data_loader.load_tickers(list(tickerSet))

slice_trader = SliceTrader()
for key, value in slices.items():
    data = slice_trader.calculate_strategy(tickers=value, daily_investment=100, start_date='11/15/2023'
                                           , rolling_window=200)

    strategy_name = key
    target_file = 'data/temp/' + strategy_name + '_investment.xlsx'
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    data.to_excel(target_file, engine='openpyxl')
