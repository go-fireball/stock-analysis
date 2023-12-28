import json

from stock_analysis.dtos.slice import Slice


class Config:
    raw_data_directory_name = 'data/raw'
    derived_data_directory_name = 'data/derived'
    tickers_config_path = './stock_analysis/config/tickers.json'
    slices_config_path = './stock_analysis/config/slices.json'

    @staticmethod
    def raw_csv_path(ticker: str) -> str:
        return "{0}/{1}.csv".format(Config.raw_data_directory_name, ticker)

    @staticmethod
    def raw_json_path(ticker) -> str:
        return "{0}/{1}.json".format(Config.raw_data_directory_name, ticker)

    @staticmethod
    def derived_csv_path(ticker) -> str:
        return "{0}/{1}.csv".format(Config.derived_data_directory_name, ticker)

    @staticmethod
    def derived_json_path(ticker) -> str:
        return "{0}/{1}.json".format(Config.derived_data_directory_name, ticker)

    @staticmethod
    def get_tickers() -> list[str]:
        with open(Config.tickers_config_path, 'r') as file:
            tickers = json.load(file)
        return tickers

    @staticmethod
    def get_slices() -> list[Slice]:
        with open(Config.slices_config_path, 'r') as file:
            data = json.load(file)
        slices = [Slice(item["name"], item["tickers"]) for item in data]
        return slices
