import os.path

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
    ]
}

# data_loader = DataLoader()
# data_loader.load_tickers(slice_tickers)

slice_trader = SliceTrader()
for key, value in slices.items():
    data = slice_trader.calculate_strategy(tickers=value, daily_investment=100, start_date='1/1/2015'
                                           , rolling_window=30)

    strategy_name = key
    target_file = 'data/temp/' + strategy_name + '_investment.xlsx'
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    data.to_excel(target_file, engine='openpyxl')
