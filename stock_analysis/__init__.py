import os

import pandas as pd

from stock_analysis.config.config import Config
from stock_analysis.dtos.slice import Slice
from stock_analysis.process.data_loader import RawDataLoader
from stock_analysis.strategy.dollar_averaging import DollarAveraging
from stock_analysis.strategy.slice_trader import SliceTrader
import yfinance as yf


def ticker_info(tickers: list[str]):
    columns = ['Market Cap (in Billions)', 'PE Ratio']
    df = pd.DataFrame(columns=columns)
    df.index.name = 'Ticker'

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        market_cap = None
        pe_ratio = None
        if stock.info.__contains__('marketCap'):
            market_cap = round(stock.info['marketCap'] / 1000000000, 3)
        if stock.info.__contains__('trailingPE'):
            pe_ratio = stock.info['trailingPE']

        df.loc[ticker] = [market_cap, pe_ratio]
    target_file = 'data/temp/ticker_info.xlsx'
    df.to_excel(target_file, engine='openpyxl')


def dollar_averaging(daily_investment=100, start_date='1/1/2000'):
    print('running dollar averaging trading for each ticker')
    daily_trader = DollarAveraging()
    data = daily_trader.calculate_strategy(tickers=Config.get_tickers(), daily_investment=daily_investment,
                                           start_date=start_date)
    target_file = 'data/temp/dollar_averaging.xlsx'
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    print('writing file {0}'.format(target_file))
    data.to_excel(target_file, engine='openpyxl')


def run_slice_trading(slices=None, daily_investment=100,
                      start_date='1/1/2000', rolling_window=200):
    print('running slice trading')
    if slices is None:
        slices = Config.get_slices()
    slice_trader = SliceTrader()
    for individualSlice in slices:
        data, data_pf = slice_trader.calculate_strategy(tickers=individualSlice.tickers,
                                                        daily_investment=daily_investment,
                                                        start_date=start_date,
                                                        rolling_window=rolling_window)
        target_file = 'data/temp/' + individualSlice.name + '_slice.xlsx'
        target_pf_file = 'data/temp/' + individualSlice.name + '_slice_pf.xlsx'
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        print('writing file {0}'.format(target_file))
        data.to_excel(target_file, engine='openpyxl')
        data_pf.to_excel(target_pf_file, engine='openpyxl')

        last_profit_percent_data = []

        for ticker in individualSlice.tickers:
            ticker_profit_percent = data[(ticker, 'Profit_%')].iloc[-1]
            last_profit_percent_data.append({'Ticker': ticker,
                                             'Last Profit %': ticker_profit_percent})

        total_profit_percent = data[('Total', 'Profit_%')].iloc[-1]
        slice_sharp_ratio = data[('Slice', 'SharpRatio.{0}'.format(rolling_window))].iloc[-1]

        last_profit_percent_data.append({'Ticker': 'Total',
                                         'Last Profit %': total_profit_percent})
        last_profit_percent_data.append({'Ticker': 'Slice Sharp Ratio',
                                         'Last Profit %': slice_sharp_ratio})

        target_file = 'data/temp/' + individualSlice.name + '_slice_summary.xlsx'
        last_profit_percent_df = pd.DataFrame(last_profit_percent_data).set_index('Ticker')
        last_profit_percent_df.to_excel(target_file, engine='openpyxl')
