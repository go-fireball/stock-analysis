import pandas as pd


class SliceTrader:
    def calculate_strategy(self, tickers, daily_investment: int):
        adj_close_data = self.__load_price(tickers)
        return self.__calculate_investment(adj_close_data, tickers, daily_investment)

    @staticmethod
    def __load_price(tickers) -> pd.DataFrame:
        adj_close_data = pd.DataFrame()

        for ticker in tickers:
            filename = 'data/' + ticker + '.csv'
            data = pd.read_csv(filename, index_col=0, parse_dates=True, usecols=["Date", "Adj Close"])
            data.rename(columns={"Adj Close": ticker}, inplace=True)

            if adj_close_data.empty:
                adj_close_data = data
            else:
                # Merge the data on the Date index
                adj_close_data = adj_close_data.join(data, how='outer')

        return adj_close_data

    @staticmethod
    def __calculate_investment(adj_close_data, tickers, daily_investment: int) -> pd.DataFrame:
        combined_data = pd.DataFrame(index=adj_close_data.index)

        total_cost = pd.Series(index=adj_close_data.index, dtype=float).fillna(0)
        total_value = pd.Series(index=adj_close_data.index, dtype=float).fillna(0)

        for ticker in tickers:
            daily_investment_per_ticker = round(daily_investment / len(tickers), 4)  # Investment per ticker
            units = daily_investment_per_ticker / adj_close_data[ticker]  # Number of units bought daily

            combined_data[(ticker, 'Adj Close')] = round(adj_close_data[ticker], 4)
            combined_data[(ticker, 'Daily Cost')] = daily_investment_per_ticker
            combined_data[(ticker, 'Total Cost')] = round(combined_data[(ticker, 'Daily Cost')].cumsum(), 4)

            combined_data[(ticker, 'Units')] = round(units.cumsum(), 4)  # Cumulative sum of units over time
            combined_data[(ticker, 'Current Value')] = round(combined_data[(ticker, 'Units')] * adj_close_data[ticker],
                                                             4)
            total_cost += daily_investment_per_ticker
            total_value += combined_data[(ticker, 'Current Value')]

        combined_data['Total', 'Cost'] = round(total_cost.cumsum(), 0)
        combined_data['Total', 'Value'] = round(total_value, 2)
        combined_data['Total', 'Profit'] = round(combined_data['Total', 'Value'] - combined_data['Total', 'Cost'], 2)
        combined_data['Total', '% age'] = round(
            combined_data['Total', 'Profit'] / combined_data['Total', 'Cost'] * 100, 2)

        combined_data.columns = pd.MultiIndex.from_tuples(combined_data.columns)  # Create a MultiIndex
        return combined_data
