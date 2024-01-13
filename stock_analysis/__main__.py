from stock_analysis import RawDataLoader, dollar_averaging, run_slice_trading, ticker_info, indexes
from stock_analysis.config.config import Config

if __name__ == "__main__":
    daily_investment = 225
    start_date = '12/29/2023'
    rolling_window = 200
    indexes()
    price_load = False
    tickers = Config.get_tickers()
    if price_load:
        data_loader = RawDataLoader()
        data_loader.load_tickers(tickers)
        ticker_info(tickers)
    dollar_averaging(daily_investment=daily_investment, start_date=start_date)
    run_slice_trading(Config.get_slices(), daily_investment=daily_investment, rolling_window=7)
    print('Process Completed')
    exit(0)
