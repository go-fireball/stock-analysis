import pandas as pd

from data_access.data_access import DataAccess


class DailyTrader:
    def __init__(self):
        self.__data_access = DataAccess()

    def calculate_strategy(self, tickers, daily_investment: int, start_date: str = '01/01/2010'):
        price_data = self.__data_access.load_price(tickers, start_date)
        combined_data = self.__calculate_investment(price_data, tickers, daily_investment)
        comparison_data = self.__save_profit_percent_to_excel(combined_data)
        return comparison_data

    @staticmethod
    def __calculate_investment(price_data, tickers, daily_investment: int) -> pd.DataFrame:
        data_frames = []

        for ticker in tickers:
            units = round(daily_investment / price_data[ticker], 4)  # Number of units bought daily
            daily_cost = round(units * price_data[ticker], 2)
            ticker_data = pd.DataFrame({
                (ticker, 'Price'): round(price_data[ticker], 4),
                (ticker, 'Units'): round(units.cumsum(), 4),
                (ticker, 'Total Cost'): round(daily_cost.cumsum(), 4),
                (ticker, 'Market Value'): round((units.cumsum()) * price_data[ticker], 4),
                (ticker, 'Profit'): round((units.cumsum() * price_data[ticker]) - daily_cost.cumsum(), 4),
                (ticker, 'Profit %'): round(
                    ((units.cumsum() * price_data[ticker]) - daily_cost.cumsum()) / daily_cost.cumsum() * 100, 4)
            })
            data_frames.append(ticker_data)
        combined_data = pd.concat(data_frames, axis=1)
        combined_data.columns = pd.MultiIndex.from_tuples(combined_data.columns)  # Create a MultiIndex
        return combined_data

    @staticmethod
    def __save_profit_percent_to_excel(combined_data) -> pd.DataFrame:
        comparison_data = pd.DataFrame(index=combined_data.index)
        # Concatenate 'Profit %' for each ticker
        for ticker in combined_data.columns.levels[0]:
            # Extracting Profit % data
            profit_percent_data = (combined_data[(ticker, 'Market Value')] - combined_data[(ticker, 'Total Cost')]) / \
                                  combined_data[(ticker, 'Total Cost')] * 100
            comparison_data[ticker] = profit_percent_data  # Adding to the comparison DataFrame
        return comparison_data
