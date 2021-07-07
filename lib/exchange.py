from abc import ABC, abstractmethod
import json
import datetime

class Exchange(ABC):

    @abstractmethod
    def get_data(): pass

    @abstractmethod
    def record_candlesticks_data(): pass

    @abstractmethod
    def record_indicators_data(): pass


class Binance(Exchange):
    def __init__(self):
        self._opens = list()
        self._closes = list()
        self._highs = list()
        self._lows = list()
        self._in_position = False
        self._last_atr = 0.0
        self._last_rsi = 0.0
    def get_data(self):
        res = {
            "date_time": str(datetime.datetime.now()),
            "indicators": {
                'rsi': self._last_rsi,
                'atr': self._last_atr
            },
            "candlestick": {
                'count_candle': len(self._closes),
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
        self._last_rsi = rsi
        self._last_atr = atr

class Coinbase(Exchange):
    def __init__(self, symbol, price):
        self.symbol = symbol
        self.price = price
    def get_data(self):
        return json.dumps({'symbol': self.symbol, 'price': self.price})
