from abc import ABC, abstractmethod
import json

class Exchange(ABC):

    @abstractmethod
    def get_data(): pass

    @abstractmethod
    def record_candlesticks_data(): pass

    @abstractmethod
    def record_indicators_data(): pass


class Binance(Exchange):
    _opens = list()
    _closes = list()
    _highs = list()
    _lows = list()
    _in_position = False
    _last_rsi = 0.0
    _last_atr = 0.0
    def get_data(self):
        res = {
            "indicators": {
                'rsi': self._last_rsi,
                'atr': self._last_atr
            },
            "candlestick": {
                'open_prices': self._opens,
                'close_prices': self._closes,
                'high_prices': self._highs,
                'low_prices': self._lows
            }
        }
        with open('last_info.json', 'w') as json_:
            json.dump(res, json_, indent=4)
        return res
    def record_candlesticks_data(self, open, close, high, low):
        self._opens.append(open)
        self._closes.append(close)
        self._highs.append(high)
        self._lows.append(low)
    def record_indicators_data(self, rsi, atr):
        self.rsi = rsi
        self.atr = atr

class Coinbase(Exchange):
    def __init__(self, symbol, price):
        self.symbol = symbol
        self.price = price
    def get_data(self):
        return json.dumps({'symbol': self.symbol, 'price': self.price})
