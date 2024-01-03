import pandas as pd
from stock_analysis.data_access.data_access import DataAccess
from stock_analysis.series.series_helper import SeriesHelper


class DollarAveraging:
    def __init__(self):
        self.__data_access = DataAccess()

    def calculate_strategy(self, tickers, daily_investment: int, start_date: str = '01/01/2010'):
        price_data = self.__data_access.load_price(tickers, start_date=start_date)
        combined_data = self.__calculate_investment(price_data, tickers, daily_investment)
        return combined_data

    @staticmethod
    def __calculate_investment(price_data, tickers, daily_investment: int) -> pd.DataFrame:
        data_frames = []

        for ticker in tickers:
            adjusted_price = round(price_data[ticker], 2)
            units = round(daily_investment / adjusted_price, 4)  # Number of units bought daily
            # noinspection DuplicatedCode
            daily_cost = round(units * adjusted_price, 2)
            total_cost = daily_cost.cumsum()
            total_value = units.cumsum() * adjusted_price

            ticker_data = pd.DataFrame({
                (ticker, 'Price'): adjusted_price,
                (ticker, 'Units'): round(units.cumsum(), 4),
                (ticker, 'Total Cost'): round(total_cost, 4),
                (ticker, 'Total Value'): round(total_value, 4),
                (ticker, 'Profit'): SeriesHelper.calculate_profit(total_cost, total_value),
                (ticker, 'Profit_%'): SeriesHelper.calculate_profit_percent(total_cost, total_value)
            })
            data_frames.append(ticker_data)
        combined_data = pd.concat(data_frames, axis=1)
        combined_data.columns = pd.MultiIndex.from_tuples(combined_data.columns)  # Create a MultiIndex
        return combined_data

