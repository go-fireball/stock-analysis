from stock_analysis.data_access.data_access import DataAccess
import pandas as pd

from stock_analysis.strategy.constants import Constants


# noinspection DuplicatedCode
class DailyUnitTrader:
    def __init__(self):
        self.__data_access = DataAccess()

    def calculate_strategy(self, tickers, start_date: str = '01/01/2010'):
        price_data = self.__data_access.load_price(tickers, start_date=start_date)
        combined_data = self.__calculate_investment(price_data, tickers)
        return combined_data

    @staticmethod
    def __calculate_investment(price_data, tickers) -> pd.DataFrame:
        data_frames = []

        for ticker in tickers:
            units = pd.Series(index=price_data.index, dtype=float).fillna(1)
            daily_cost = round(units * price_data[ticker], 2)
            ticker_data = pd.DataFrame({
                (ticker, Constants.Price): round(price_data[ticker], 4),
                (ticker, Constants.Units): round(units.cumsum(), 4),
                (ticker, Constants.TotalCost): round(daily_cost.cumsum(), 4),
                (ticker, Constants.TotalValue): round((units.cumsum()) * price_data[ticker], 4),
                (ticker, Constants.Profit): round((units.cumsum() * price_data[ticker]) - daily_cost.cumsum(), 4),
                (ticker, Constants.ProfitPercent): round(
                    ((units.cumsum() * price_data[ticker]) - daily_cost.cumsum()) / daily_cost.cumsum() * 100, 4)
            })
            data_frames.append(ticker_data)
        combined_data = pd.concat(data_frames, axis=1)
        combined_data.columns = pd.MultiIndex.from_tuples(combined_data.columns)  # Create a MultiIndex
        return combined_data
