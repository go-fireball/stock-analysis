import pandas as pd

from data_access.data_access import DataAccess


class SliceTrader:
    def __init__(self):
        self.__data_access = DataAccess()

    def calculate_strategy(self, tickers, daily_investment: int, start_date: str = '01/01/2010', rolling_window=30):
        adj_close_data = self.__data_access.load_price(tickers, start_date)
        portfolio_data = self.__calculate_investment(adj_close_data, tickers, daily_investment)
        return self.__calculate_risk(portfolio_data, daily_investment, rolling_window)

    @staticmethod
    def __calculate_risk(portfolio_data, daily_investment, rolling_window) -> pd.DataFrame:
        risk_free_rate = 0.04
        total_return = portfolio_data['Total', 'Value'] / (portfolio_data['Total', 'Cost'].shift(
            1) + daily_investment) - 1

        rolling_std_dev = total_return.rolling(window=rolling_window).std()
        rolling_mean_return = total_return.rolling(window=rolling_window).mean()
        rolling_sharpe_ratio = (rolling_mean_return - risk_free_rate) / rolling_std_dev
        rolling_sharpe_ratio[rolling_std_dev == 0] = None

        returns = portfolio_data['Total', 'Value'] / (portfolio_data['Total', 'Cost'].shift(
            1) + daily_investment) - 1
        excess_returns = returns - risk_free_rate

        negative_excess_returns = excess_returns.loc[excess_returns < 0]
        rolling_negative_std_dev = negative_excess_returns.rolling(window=rolling_window).std()
        rolling_mean_excess_return = excess_returns.rolling(window=rolling_window).mean()
        rolling_sortino_ratio = rolling_mean_excess_return / rolling_negative_std_dev
        mask = (rolling_negative_std_dev == 0).reindex(rolling_sortino_ratio.index, fill_value=False)
        rolling_sortino_ratio[mask] = None

        portfolio_data['Total', 'TotalReturn'] = total_return
        portfolio_data['Total', 'SharpRation'] = rolling_sharpe_ratio
        portfolio_data['Total', 'SortinoRatio'] = rolling_sortino_ratio

        return portfolio_data

    @staticmethod
    def __calculate_investment(adj_close_data, tickers, daily_investment: int) -> pd.DataFrame:
        combined_data = pd.DataFrame(index=adj_close_data.index)

        total_cost = pd.Series(index=adj_close_data.index, dtype=float).fillna(0)
        total_value = pd.Series(index=adj_close_data.index, dtype=float).fillna(0)

        for ticker in tickers:
            daily_investment_per_ticker = round(daily_investment / len(tickers), 4)  # Investment per ticker
            units = daily_investment_per_ticker / adj_close_data[ticker]  # Number of units bought daily

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
