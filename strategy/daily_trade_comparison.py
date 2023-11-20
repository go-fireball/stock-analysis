import pandas as pd


class DailyTrader:
    def calculate_strategy(self, tickers, daily_investment: int):
        price_data = self.__load_price(tickers)
        combined_data = self.__calculate_investment(price_data, tickers, daily_investment)
        comparison_data = self.__save_profit_percent_to_excel(combined_data)
        return comparison_data

    @staticmethod
    def __load_price(tickers) -> pd.DataFrame:
        price_data = pd.DataFrame()

        for ticker in tickers:
            filename = 'data/' + ticker + '.csv'
            data = pd.read_csv(filename, index_col=0, parse_dates=True, usecols=["Date", "High"])
            data.rename(columns={"High": ticker}, inplace=True)

            if price_data.empty:
                price_data = data
            else:
                # Merge the data on the Date index
                price_data = price_data.join(data, how='outer')

        return price_data

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
