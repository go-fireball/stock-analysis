import os.path
import typing

import numpy as np
import pandas as pd
import yfinance as yf
from arch import arch_model


class DataLoader:
    def load_tickers(self, tickers: typing.List):
        for ticker in tickers:
            self.load_historical(ticker)

    def load_historical(self, ticker: str):
        start_date = "2010-01-01"
        filename = 'data/raw/' + ticker + '.csv'
        if os.path.exists(filename):
            existing_data = pd.read_csv(filename, index_col=0, parse_dates=True)
            last_date = existing_data.index[-1]

            adjusted_last_date = last_date - pd.Timedelta(days=5)
            new_data = yf.download(ticker, start=adjusted_last_date)
            combined_data = pd.concat([existing_data, new_data])
            combined_data = combined_data[~combined_data.index.duplicated(keep='last')]
        else:
            new_data = yf.download(ticker, start=start_date)
            combined_data = new_data

        combined_data.sort_index(inplace=True)
        combined_data['High_STD'] = combined_data['High'].rolling(window=len(combined_data), min_periods=1).std()
        combined_data['Return'] = combined_data['High'].pct_change()
        combined_data['Actual_Volatility'] = combined_data['Return'].rolling(window=30).std()

        garch = arch_model(combined_data['Return'].dropna(), vol="GARCH", p=1, q=1, rescale=False)
        res = garch.fit(disp='off')
        forecast = res.forecast(horizon=30, start=start_date, align='target')
        garch_volatility_series = pd.Series(np.nan, index=combined_data.index)
        forecast_dates = forecast.variance.dropna().index
        garch_volatility_series.loc[forecast_dates] = np.sqrt(forecast.variance.dropna()['h.21']) * np.sqrt(252)
        combined_data['GARCH_Volatility'] = garch_volatility_series
        self.save_data(combined_data, filename)

    @staticmethod
    def save_data(data: pd.DataFrame, filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # Save the data to a CSV file
        data.to_csv(filename)

