from stock_analysis import RawDataLoader, dollar_averaging, run_slice_trading
from stock_analysis.config.config import Config

if __name__ == "__main__":
    daily_investment = 100
    start_date = '1/1/2010'
    price_load = False
    tickers = Config.get_tickers()
    if price_load:
        data_loader = RawDataLoader()
        data_loader.load_tickers(tickers)
    dollar_averaging(daily_investment=daily_investment, start_date=start_date)
    run_slice_trading(Config.get_slices(), daily_investment=daily_investment, start_date=start_date)
    print('Process Completed')
    exit(0)
