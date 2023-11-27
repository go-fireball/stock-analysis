import pandas as pd


class DataAccess:

    @staticmethod
    def load_price(tickers, start_date: str = '01/01/2010') -> pd.DataFrame:
        data_frames = []

        for ticker in tickers:
            filename = 'data/' + ticker + '.csv'
            data = pd.read_csv(filename, index_col=0, parse_dates=True, usecols=["Date", "High"])
            data.rename(columns={"High": ticker}, inplace=True)
            data = data[data.index >= pd.to_datetime(start_date)]

            # Check for duplicate indices and handle them
            if data.index.duplicated().any():
                print(f"Duplicate indices found in {ticker}. Handling duplicates.")
                # Choose a method to handle duplicates, for example, dropping them
                data = data[~data.index.duplicated(keep='first')]
            data_frames.append(data)

        price_data = pd.concat(data_frames, axis=1)
        return price_data
