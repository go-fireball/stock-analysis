from stock_analysis import RawDataLoader, dollar_averaging, run_slice_trading
from stock_analysis.config.config import Config

if __name__ == "__main__":
    tickers = Config.get_tickers()
    data_loader = RawDataLoader()
    data_loader.load_tickers(tickers)
    dollar_averaging(daily_investment=100, start_date='1/1/2010')
    run_slice_trading(Config.get_slices(), start_date='1/1/2010')
    print('Process Completed')
    exit(0)
