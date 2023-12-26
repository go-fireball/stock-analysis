class Slice:
    tickers: list[str]
    name: str

    def __init__(self, name: str, tickers: list[str]):
        self.name = name
        self.tickers = tickers
