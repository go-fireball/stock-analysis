from typing import Any

import pandas as pd

from stock_analysis.data_access.data_access import DataAccess


class SliceTrader:
    def __init__(self):
        self.__data_access = DataAccess()

    def calculate_strategy(self, tickers, daily_investment: int,
                           start_date: str = '01/01/2010',
                           rolling_window=30) -> (pd.DataFrame, pd.DataFrame):
        adj_close_data = self.__data_access.load_price(tickers, start_date=start_date)
        portfolio_data = self.__calculate_investment(adj_close_data, tickers, daily_investment)
        analysis_data = self.__calculate_risk(portfolio_data, rolling_window)
        analysis_data['Slice', 'Price'] = self.__calculate_slice_price(adj_close_data, tickers)
        analysis_data['Slice', 'Index'] = self.__calculate_index(adj_close_data)
        annual_profit_df = self.calculate_annualized_profit_improved(portfolio_data)
        return analysis_data, annual_profit_df

    @staticmethod
    def __calculate_slice_price(adj_close_data: pd.DataFrame, tickers) -> pd.DataFrame:
        weight_per_ticker = 1 / len(tickers)
        weighted_prices = adj_close_data.apply(lambda x: x * weight_per_ticker)
        slice_price = weighted_prices.sum(axis=1)
        return slice_price

    @staticmethod
    def __calculate_index(adj_close_data: pd.DataFrame) -> pd.DataFrame:
        normalized_data = (adj_close_data / adj_close_data.iloc[0])
        equal_weighted_index = normalized_data.mean(axis=1) * 100
        return equal_weighted_index

    @staticmethod
    def __calculate_total_return(cost_series: pd.Series, value_series: pd.Series) -> pd.Series:
        total_return = (value_series / cost_series) - 1
        return round(total_return, 4)

    @staticmethod
    def __calculate_sharp_ratio(total_return: pd.Series, annual_risk_free_rate: float,
                                rolling_window: int) -> pd.Series:
        daily_risk_free_rate = (1 + annual_risk_free_rate) ** (1 / 252) - 1  # Assuming 252 trading days in a year
        rolling_std_dev = total_return.rolling(window=rolling_window).std()
        rolling_mean_return = total_return.rolling(window=rolling_window).mean()
        rolling_sharpe_ratio = (rolling_mean_return - daily_risk_free_rate) / rolling_std_dev
        rolling_sharpe_ratio[rolling_std_dev == 0] = None
        return round(rolling_sharpe_ratio, 2)

    @staticmethod
    def __calculate_sortino_ratio(total_return: pd.Series, annual_risk_free_rate: float,
                                  rolling_window: int) -> pd.Series:
        daily_risk_free_rate = (1 + annual_risk_free_rate) ** (1 / 252) - 1
        excess_returns = total_return - daily_risk_free_rate
        negative_excess_returns = excess_returns.loc[excess_returns < 0]
        rolling_negative_std_dev = negative_excess_returns.rolling(window=rolling_window).std()
        rolling_mean_excess_return = excess_returns.rolling(window=rolling_window).mean()
        rolling_sortino_ratio = rolling_mean_excess_return / rolling_negative_std_dev
        mask = (rolling_negative_std_dev == 0).reindex(rolling_sortino_ratio.index, fill_value=False)
        rolling_sortino_ratio[mask] = None
        return round(rolling_sortino_ratio, 2)

    @staticmethod
    def __calculate_risk(portfolio_data: pd.DataFrame, rolling_window: int) -> pd.DataFrame:
        total_return = SliceTrader.__calculate_total_return(portfolio_data['Total', 'Cost'],
                                                            portfolio_data['Total', 'Value'])
        annual_risk_free_rate: float = 0.05
        rolling_sharpe_ratio = SliceTrader.__calculate_sharp_ratio(total_return=total_return,
                                                                   annual_risk_free_rate=annual_risk_free_rate,
                                                                   rolling_window=rolling_window)
        rolling_sortino_ratio = SliceTrader.__calculate_sortino_ratio(total_return=total_return,
                                                                      annual_risk_free_rate=annual_risk_free_rate,
                                                                      rolling_window=rolling_window)
        portfolio_data['Slice', 'TotalReturn'] = total_return
        portfolio_data['Slice', 'SharpRatio.{0}'.format(rolling_window)] = rolling_sharpe_ratio
        portfolio_data['Slice', 'SortinoRatio.{0}'.format(rolling_window)] = rolling_sortino_ratio

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

            combined_data[(ticker, 'Profit')] = round(combined_data[(ticker, 'Current Value')] -
                                                      combined_data[(ticker, 'Total Cost')], 2)
            combined_data[(ticker, 'Profit_%')] = round(
                combined_data[(ticker, 'Profit')] / combined_data[(ticker, 'Total Cost')] * 100, 2)
            total_cost += daily_investment_per_ticker
            total_value += combined_data[(ticker, 'Current Value')]

        combined_data['Total', 'Cost'] = round(total_cost.cumsum(), 0)
        combined_data['Total', 'Value'] = round(total_value, 2)
        combined_data['Total', 'Profit'] = round(combined_data['Total', 'Value'] - combined_data['Total', 'Cost'], 2)
        combined_data['Total', 'Profit_%'] = round(
            combined_data['Total', 'Profit'] / combined_data['Total', 'Cost'] * 100, 2)

        combined_data.columns = pd.MultiIndex.from_tuples(combined_data.columns)  # Create a MultiIndex
        return combined_data

    @staticmethod
    def calculate_annualized_profit_improved(combined_data: pd.DataFrame) -> pd.DataFrame:
        def annualized_return(x):
            if len(x) < 2:
                return None
            start_date = x.index[0]
            end_date = x.index[-1]
            years = (end_date - start_date).days / 365.25
            if years <= 0:
                return None
            return ((x.iloc[-1] + 1) ** (1 / years) - 1) * 100

        total_return = combined_data['Slice', 'TotalReturn']
        annual_profit = total_return.groupby(pd.Grouper(freq='Y')).apply(annualized_return)
        annual_profit_df = annual_profit.to_frame('Annualized Profit %')
        annual_profit_df.index = annual_profit_df.index.year
        return annual_profit_df
