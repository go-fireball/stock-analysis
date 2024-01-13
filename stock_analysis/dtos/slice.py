class Slice:
    tickers: list[str]
    name: str
    start_date: str

    def __init__(self, name: str, tickers: list[str], start_date: str):
        self.name = name
        self.tickers = tickers
        self.start_date = start_date
