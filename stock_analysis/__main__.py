from typing import List, Tuple

from stock_analysis import RawDataLoader, dollar_averaging, run_slice_trading, ticker_info, indexes
from stock_analysis.config.config import Config
from datetime import datetime

daily_investment_pairs: list[tuple[datetime, int]] = [
    (datetime(2023, 12, 29), 225),
    (datetime(2024, 2, 1), 270),
]

# write a function such that given a date string, it should fetch the investment amount, from the daily_investment_pairs
# such that start from datetime(2023, 12, 29) it should return 225 until datetime(2024, 2, 1), from datetime(2024, 2, 1)
# it should return 300 and so on


if __name__ == "__main__":
    daily_investment = 225
    start_date = '12/29/2023'
    rolling_window = 200
    indexes()
    price_load = True
    tickers = Config.get_tickers()
    if price_load:
        data_loader = RawDataLoader()
        data_loader.load_tickers(tickers)
        ticker_info(tickers)
    dollar_averaging(daily_investment=daily_investment, start_date=start_date)
    run_slice_trading(daily_investment_pairs=daily_investment_pairs,
                      slices=Config.get_slices(), rolling_window=7)
    print('Process Completed')
    exit(0)
