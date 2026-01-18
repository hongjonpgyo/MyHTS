# app/core/ls_market_cache_core.py
class MarketCache:
    def __init__(self):
        self.prices = {}

    def set_price(self, symbol, price, change=None, change_rate=None):
        self.prices[symbol] = {
            "price": price,
            "change": change,
            "change_rate": change_rate,
        }

    def get_price(self, symbol):
        return self.prices.get(symbol)
