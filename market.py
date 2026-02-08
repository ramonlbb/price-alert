import yfinance as yf

ALERTS_FILE = "alerts.json"


def get_price(symbol: str) -> float:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")

    if data.empty:
        raise Exception(f"Sem dados para {symbol}")

    return float(data["Close"].iloc[-1])
