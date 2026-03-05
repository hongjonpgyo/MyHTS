from dataclasses import dataclass


@dataclass
class SymbolMeta:
    symbol: str
    tick_size: float
    multiplier: float


class SymbolMetaCache:

    def __init__(self):
        self._data: dict[str, SymbolMeta] = {}

    # ---------------------------------
    # set
    # ---------------------------------
    def set(self, symbol: str, meta: SymbolMeta):
        if not symbol:
            return

        self._data[symbol] = meta

    # ---------------------------------
    # get
    # ---------------------------------
    def get(self, symbol: str) -> SymbolMeta | None:
        return self._data.get(symbol)

    # ---------------------------------
    # tick_size
    # ---------------------------------
    def tick_size(self, symbol: str) -> float:

        meta = self.get(symbol)

        if not meta:
            return 1.0

        return meta.tick_size

    # ---------------------------------
    # multiplier
    # ---------------------------------
    def multiplier(self, symbol: str) -> float:

        meta = self.get(symbol)

        if not meta:
            return 1.0

        return meta.multiplier

    # ---------------------------------
    # price normalize
    # ---------------------------------
    def normalize_price(self, symbol: str, price: float) -> float:

        tick = self.tick_size(symbol)

        if tick <= 0:
            return price

        normalized = round(price / tick) * tick

        return round(normalized, 10)

    # ---------------------------------
    # price up (1 tick)
    # ---------------------------------
    def price_up(self, symbol: str, price: float) -> float:

        tick = self.tick_size(symbol)

        return round(price + tick, 10)

    # ---------------------------------
    # price down (1 tick)
    # ---------------------------------
    def price_down(self, symbol: str, price: float) -> float:

        tick = self.tick_size(symbol)

        return round(price - tick, 10)

    # ---------------------------------
    # clear
    # ---------------------------------
    def clear(self):
        self._data.clear()

    # ---------------------------------
    # size
    # ---------------------------------
    def size(self):
        return len(self._data)


# ---------------------------------
# global singleton
# ---------------------------------
symbol_meta_cache = SymbolMetaCache()