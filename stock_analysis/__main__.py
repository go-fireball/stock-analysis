from datetime import datetime

from stock_analysis import RawDataLoader, dollar_averaging, run_slice_trading, ticker_info, indexes, run_unit_trading
from stock_analysis.config.config import Config

daily_investment_pairs: list[tuple[datetime, int]] = [
    (datetime(2009, 12, 29), 100),
    (datetime(2023, 12, 29), 225),
    (datetime(2024, 2, 1), 270),
    (datetime(2024, 3, 1), 315),
]
start_date = '12/29/2023'

if __name__ == "__main__":
    start_date = '12/29/2023'
    rolling_window = 200
    indexes()
    price_load = True
    tickers = Config.get_tickers()
    if price_load:
        data_loader = RawDataLoader()
        data_loader.load_tickers(tickers)
        ticker_info(tickers)
    dollar_averaging(daily_investment_pairs=daily_investment_pairs, start_date=start_date)
    dollar_averaging(daily_investment_pairs=daily_investment_pairs, start_date='1/1/2015')
    run_slice_trading(daily_investment_pairs=daily_investment_pairs,
                      slices=Config.get_slices(), rolling_window=7)
    run_unit_trading(tickers=tickers, start_date=start_date)
    run_unit_trading(tickers=tickers, start_date='1/1/2010')
    print('Process Completed')
    exit(0)
