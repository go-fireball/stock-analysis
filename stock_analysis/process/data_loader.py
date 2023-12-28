import os.path
import typing

import numpy as np
import pandas as pd
import yfinance as yf
from arch import arch_model

from stock_analysis.config.config import Config


class RawDataLoader:

    def load_tickers(self, tickers: typing.List):
        for ticker in tickers:
            raw_data = self.load_historical(ticker)
            self.save_raw_data(raw_data, ticker)
            derived_data = self.generate_derived_data(ticker)
            self.save_derived_data(derived_data, ticker)

    @staticmethod
    def load_historical(ticker: str) -> pd.DataFrame:
        start_date = "1960-01-01"
        print('Downloading {0} Price Information'.format(ticker))
        if os.path.exists(Config.raw_csv_path(ticker)):
            existing_data = pd.read_csv(Config.raw_csv_path(ticker),
                                        index_col=0, parse_dates=True)
            last_date = existing_data.index[-1]

            adjusted_last_date = last_date - pd.Timedelta(days=5)
            new_data = yf.download(ticker, start=adjusted_last_date)
            combined_data = pd.concat([existing_data, new_data])
            combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
        else:
            new_data = yf.download(ticker, start=start_date)
            combined_data = new_data
        combined_data.sort_index(inplace=True)
        return combined_data

    @staticmethod
    def save_raw_data(data: pd.DataFrame, ticker: str):
        os.makedirs(os.path.dirname(Config.raw_csv_path(ticker)), exist_ok=True)
        data.to_csv(Config.raw_csv_path(ticker))
        # data.to_json(self.raw_json_path(ticker))

    @staticmethod
    def save_derived_data(data: pd.DataFrame, ticker: str):
        os.makedirs(os.path.dirname(Config.derived_csv_path(ticker)), exist_ok=True)
        data.to_csv(Config.derived_csv_path(ticker))
        data.to_json(Config.derived_json_path(ticker))

    @staticmethod
    def generate_derived_data(ticker) -> pd.DataFrame:
        combined_data = pd.read_csv(Config.raw_csv_path(ticker), index_col=0, parse_dates=True)
        combined_data.sort_index(inplace=True)
        combined_data['Open'] = combined_data['Open'].round(4)
        combined_data['High'] = combined_data['High'].round(4)
        combined_data['Low'] = combined_data['Low'].round(4)
        combined_data['Close'] = combined_data['Close'].round(4)
        combined_data['Adj Close'] = combined_data['Adj Close'].round(4)
        combined_data['MVA.20'] = combined_data['High'].rolling(window=30).mean().round(4)
        combined_data['MVA.20'] = combined_data['High'].rolling(window=30).mean().round(4)
        combined_data['MVA.30'] = combined_data['High'].rolling(window=30).mean().round(4)
        combined_data['MVA.60'] = combined_data['High'].rolling(window=60).mean().round(4)
        combined_data['MVA.90'] = combined_data['High'].rolling(window=90).mean().round(4)
        combined_data['MVA.120'] = combined_data['High'].rolling(window=120).mean().round(4)
        combined_data['MVA.180'] = combined_data['High'].rolling(window=180).mean().round(4)
        combined_data['Std.2'] = combined_data['High'].rolling(window=2).std().round(4)
        combined_data['Std.5'] = combined_data['High'].rolling(window=5).std().round(4)
        combined_data['Std.30'] = combined_data['High'].rolling(window=30).std().round(4)

        combined_data['Return.daily'] = round(combined_data['High'].pct_change(), 4)
        combined_data['Actual_Volatility.30'] = combined_data['Return.daily'].rolling(window=30).std().round(4)

        garch = arch_model(combined_data['Return.daily'].dropna(), vol="GARCH", p=1, q=1, rescale=False)
        res = garch.fit(disp='off')
        forecast = res.forecast(horizon=30, align='target')
        garch_volatility_series = pd.Series(np.nan, index=combined_data.index)
        forecast_dates = forecast.variance.dropna().index
        garch_volatility_series.loc[forecast_dates] = np.sqrt(forecast.variance.dropna()['h.21']) * np.sqrt(252)
        combined_data['GARCH_Volatility.30'] = garch_volatility_series.round(4)
        os.makedirs(os.path.dirname(Config.derived_json_path(ticker)), exist_ok=True)
        # Save the data to a CSV file
        return combined_data
