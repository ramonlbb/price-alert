import yfinance as yf


def get_price(symbol: str) -> float | None:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="5d")

    if data.empty:
        return None

    price = data["Close"].dropna()
    if price.empty:
        return None

    # arredondamento limpo (2 casas)
    return round(float(price.iloc[-1]), 2)
