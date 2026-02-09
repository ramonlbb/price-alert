import yfinance as yf


def get_price(symbol: str) -> float | None:
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="5d")

        if data.empty:
            return None

        prices = data["Close"].dropna()

        if prices.empty:
            return None

        # 🔢 arredondamento padrão (2 casas)
        return round(float(prices.iloc[-1]), 2)

    except Exception as e:
        print(f"⚠️ Erro ao obter preço de {symbol}: {e}")
        return None
