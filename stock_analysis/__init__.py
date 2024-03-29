from datetime import datetime

import os

import pandas as pd
import pytz
from stock_analysis.config.config import Config
from stock_analysis.dtos.slice import Slice
from stock_analysis.process.data_loader import RawDataLoader
from stock_analysis.strategy.daily_unit_trader import DailyUnitTrader
from stock_analysis.strategy.dollar_averaging import DollarAveraging
from stock_analysis.strategy.slice_trader import SliceTrader
from datetime import date
import yfinance as yf


def indexes():
    indices = {
        '^GSPC': 'S&P 500 (US)',
        '^DJI': 'Dow Jones Industrial Average (US)',
        '^IXIC': 'NASDAQ Composite (US)',
        '^FTSE': 'FTSE 100 (UK)',
        '^GDAXI': 'DAX (Germany)',
        '^FCHI': 'CAC 40 (France)',
        '^N225': 'Nikkei 225 (Japan)',
        '000001.SS': 'SSE Composite Index (China)',
        '^NSEI': 'NIFTY 50 (India)',
        '^BSESN': 'BSE SENSEX(India)'
    }
    columns = ['Last Close', 'Previous Close', 'Change', 'Direction', 'Last Close Time']
    df = pd.DataFrame(columns=columns)
    df.index.name = 'Index'
    for ticker, name in indices.items():
        print(ticker)
        ticker = yf.Ticker(ticker)
        hist = ticker.history(period="2d")  # Get the last 2 days

        last_close = hist['Close'].iloc[-1]
        # Check if previous close data exists
        # print(len(hist))
        if len(hist) > 1:
            previous_close = hist['Close'].iloc[-2]
            change = last_close - previous_close
            change_percent = round(change / previous_close * 100, 2)
            direction = "Up" if change > 0 else "Down" if change < 0 else "No Change"
        else:
            previous_close = None
            change = None
            change_percent = None
            direction = "Data Unavailable"

        local_time_zone = pytz.timezone('America/New_York')
        last_close_time = hist.index[-1]
        last_close_time_naive = last_close_time.replace(tzinfo=None)

        # Add data to DataFrame
        if previous_close is not None and change is not None:
            df.loc[name] = [last_close, previous_close, change_percent, direction, last_close_time_naive]
    target_file = 'data/temp/world_market_today.xlsx'
    df.to_excel(target_file, engine='openpyxl')

    formatted_date = date.today().strftime('%Y-%m-%d')
    target_file = 'data/temp/world_market_{0}.xlsx'.format(formatted_date)
    df.to_excel(target_file, engine='openpyxl')
    print(df)


def ticker_info(tickers: list[str]):
    key_to_column = {
        'marketCap': 'Market Cap (in Billions)',
        'trailingPE': 'PE Ratio',
        'returnOnEquity': 'ROE',
        'debtToEquity': 'DebtToEquity',
        'currentRatio': 'CurrentRatio',
        'operatingMargins': 'OperatingMargins',
        'freeCashflow': 'FreeCashflow',
        'revenuePerShare': 'RevenuePerShare',
        'trailingPegRatio': 'TrailingPegRatio',
        'earningsGrowth': 'EarningsGrowth',
        'revenueGrowth': 'RevenueGrowth',
        'ebitdaMargins': 'EbitdaMargins',
        'recommendationKey': 'RecommendationKey',
        'numberOfAnalystOpinions': 'NumberOfAnalystOpinions',
        'priceToBook': 'PriceToBook',
        'ebitda': 'Ebitda',
        'heldPercentInstitutions': 'HeldPercentInstitutions'
    }
    columns = list(key_to_column.values())
    df = pd.DataFrame(columns=columns)
    df.index.name = 'Ticker'

    for ticker in tickers:
        stock = yf.Ticker(ticker)
        data = {key: None for key in columns}
        info = stock.info
        for key, column in key_to_column.items():
            if key in info:
                value = info[key]
            # Special handling for marketCap (convert to billions and round)
            if key == 'marketCap' and value is not None:
                value = round(value / 1000000000, 3)
            data[column] = value

        # Replace None with pd.NA for missing values
        for key in data:
            if data[key] is None:
                data[key] = pd.NA

        df.loc[ticker] = pd.Series(data)

    target_file = 'data/temp/ticker_info.xlsx'
    df.to_excel(target_file, engine='openpyxl')


def dollar_averaging(daily_investment_pairs: list[tuple[datetime, int]], start_date='1/1/2000'):
    print('running dollar averaging trading for each ticker')
    daily_trader = DollarAveraging()
    tickers = Config.get_tickers()
    data = daily_trader.calculate_strategy(tickers=tickers, daily_investment_pairs=daily_investment_pairs,
                                           start_date=start_date)
    calculate_summary(data, start_date, tickers, 'dollar_averaging')


def calculate_summary(data, start_date, tickers, file_prefix: str):
    formatted_date = datetime.strptime(start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
    target_file = 'data/temp/{0}_{1}.xlsx'.format(file_prefix, formatted_date)
    target_summary_file = 'data/temp/{0}_summary_{1}.xlsx'.format(file_prefix, formatted_date)
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    print('writing file {0}'.format(target_file))
    data.to_excel(target_file, engine='openpyxl')
    last_profit_percent_data = []
    for ticker in tickers:
        ticker_profit_percent = data[(ticker, 'Profit_%')].iloc[-1]
        last_profit_percent_data.append({'Ticker': ticker,
                                         'Last Profit %': ticker_profit_percent})
    last_profit_percent_df = pd.DataFrame(last_profit_percent_data).set_index('Ticker')
    last_profit_percent_df.to_excel(target_summary_file, engine='openpyxl')


def run_slice_trading(daily_investment_pairs: list[tuple[datetime, int]],
                      slices=None,
                      rolling_window=200):
    print('running slice trading')
    if slices is None:
        slices = Config.get_slices()
    slice_trader = SliceTrader()
    for individualSlice in slices:
        data, data_pf = slice_trader.calculate_strategy(tickers=individualSlice.tickers,
                                                        daily_investment_pairs=daily_investment_pairs,
                                                        start_date=individualSlice.start_date,
                                                        rolling_window=rolling_window)
        formatted_date = datetime.strptime(individualSlice.start_date, '%m/%d/%Y').strftime('%Y-%m-%d')
        target_file = 'data/temp/{0}_slice_{1}.xlsx'.format(individualSlice.name, formatted_date)
        target_pf_file = 'data/temp/{0}_slice_pf_{1}.xlsx'.format(individualSlice.name, formatted_date)
        target_summary_file = 'data/temp/{0}_slice_summary_{1}.xlsx'.format(individualSlice.name, formatted_date)
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

        last_profit_percent_df = pd.DataFrame(last_profit_percent_data).set_index('Ticker')
        last_profit_percent_df.to_excel(target_summary_file, engine='openpyxl')


def run_unit_trading(tickers, start_date='1/1/2000'):
    print('running unit trading')
    daily_unit_trader = DailyUnitTrader()
    data = daily_unit_trader.calculate_strategy(tickers=tickers, start_date=start_date)
    calculate_summary(data, start_date, tickers, 'daily_unit_trading')
