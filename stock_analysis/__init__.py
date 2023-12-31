import os

import pandas as pd

from stock_analysis.config.config import Config
from stock_analysis.dtos.slice import Slice
from stock_analysis.process.data_loader import RawDataLoader
from stock_analysis.strategy.daily_trader import DailyTrader
from stock_analysis.strategy.slice_trader import SliceTrader


def dollar_averaging(daily_investment=100, start_date='1/1/2000'):
    print('running dollar averaging trading for each ticker')
    daily_trader = DailyTrader()
    data = daily_trader.calculate_strategy(tickers=Config.get_tickers(), daily_investment=daily_investment,
                                           start_date=start_date)
    target_file = 'data/temp/dollar_averaging.xlsx'
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    print('writing file {0}'.format(target_file))
    data.to_excel(target_file, engine='openpyxl')


def run_slice_trading(slices=None, daily_investment=100,
                      start_date='1/1/2000'):
    print('running slice trading')
    if slices is None:
        slices = Config.get_slices()
    slice_trader = SliceTrader()
    for individualSlice in slices:
        data = slice_trader.calculate_strategy(tickers=individualSlice.tickers,
                                               daily_investment=daily_investment,
                                               start_date=start_date,
                                               rolling_window=200)
        target_file = 'data/temp/' + individualSlice.name + '_slice.xlsx'
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        print('writing file {0}'.format(target_file))
        data.to_excel(target_file, engine='openpyxl')

        last_profit_percent_data = []

        for ticker in individualSlice.tickers:
            last_profit_percent = data[(ticker, 'Profit_%')].iloc[-1]
            last_profit_percent_data.append({'Ticker': ticker,
                                             'Last Profit %': last_profit_percent})

        last_profit_percent = data[('Total', '% age')].iloc[-1]
        last_profit_percent_data.append({'Ticker': 'Total',
                                         'Last Profit %': last_profit_percent})
        target_file = 'data/temp/' + individualSlice.name + '_slice_summary.xlsx'
        last_profit_percent_df = pd.DataFrame(last_profit_percent_data).set_index('Ticker')
        last_profit_percent_df.to_excel(target_file, engine='openpyxl')
