import pandas as pd


class SeriesHelper:

    @staticmethod
    def calculate_total_return(cost_series: pd.Series, value_series: pd.Series) -> pd.Series:
        total_return = (value_series / cost_series) - 1
        return round(total_return, 4)

    @staticmethod
    def calculate_sharp_ratio(total_return: pd.Series, annual_risk_free_rate: float,
                              rolling_window: int) -> pd.Series:
        daily_risk_free_rate = (1 + annual_risk_free_rate) ** (1 / 252) - 1  # Assuming 252 trading days in a year
        rolling_std_dev = total_return.rolling(window=rolling_window).std()
        rolling_mean_return = total_return.rolling(window=rolling_window).mean()
        rolling_sharpe_ratio = (rolling_mean_return - daily_risk_free_rate) / rolling_std_dev
        rolling_sharpe_ratio[rolling_std_dev == 0] = None
        return round(rolling_sharpe_ratio, 2)

    @staticmethod
    def calculate_sortino_ratio(total_return: pd.Series, annual_risk_free_rate: float,
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
    def calculate_annualized_profit(total_return: pd.Series) -> pd.DataFrame:
        def annualized_return(x):
            if len(x) < 2:
                return None
            start_date = x.index[0]
            end_date = x.index[-1]
            years = (end_date - start_date).days / 365.25
            if years <= 0:
                return None
            return ((x.iloc[-1] + 1) ** (1 / years) - 1) * 100

        annual_profit = total_return.groupby(pd.Grouper(freq='Y')).apply(annualized_return)
        annual_profit_df = annual_profit.to_frame('Annualized Profit %')
        annual_profit_df.index = annual_profit_df.index.year
        return annual_profit_df
