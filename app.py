from os import close
import websocket, json
import numpy as np
import talib
import telegram_send
import datetime

dt = datetime.datetime.now()
dt = dt.strftime("%d.%m|%H:%M")

# Global constants
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"
RSI_PERIOD = 14
ATR_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
RSI_MIDDLE = 50
TIMEFRAME = '1m'
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.05
long = '↗️'
short = '↘️'
stop = '⏹'
profit = '🆗'

# Global variables
closes = list()
highs = list()
lows = list()
in_position = False

def on_open(ws):
    telegram_send.send(messages=[f'[{dt}] [SERVER] \nConnection is open'])

def on_close(ws):
    telegram_send.send(messages=[f'[{dt}] [SERVER] \nConnection is close'])

def on_message(ws, msg):
    global closes, in_position, highs, lows

    json_msg = json.loads(msg)
    candle = json_msg['k']
    is_candle_closed = candle['x']
    close_price = float(candle['c'])
    high_price = float(candle['h'])
    low_price = float(candle['l'])

    # msg_t = """[{}] [RSI ALERT] \n[{} {}]\nOverbought SHORT order
    # {} entry price: {:.3f}$
    # {} take-profit: {:.3f}$
    # {} stop-loss:   {:.3f}$""".format(dt, TRADE_SYMBOL, TIMEFRAME, short, close_price, profit, 1234.4, stop, 5000.44)
    # telegram_send.send(messages=[msg_t])

    if is_candle_closed:
        closes.append(close_price)
        highs.append(high_price)
        lows.append(low_price)
        print("close price: {}, high price: {}, low price: {}".format(close_price, high_price, low_price))

        if len(closes) > RSI_PERIOD:
            np_closes = np.array(closes)
            np_highs = np.array(highs)
            np_lows = np.array(lows)
            rsi = talib.RSI(np_closes, timeperiod=RSI_PERIOD)
            atr = talib.ATR(np_highs, np_lows, np_closes, timeperiod=ATR_PERIOD)
            last_rsi = rsi[-1]
            last_atr = atr[-1]

            if last_rsi > RSI_OVERBOUGHT: 
                stop_price = close_price + (float(last_atr) * 2.00)
                profit_price = close_price - ((stop_price-close_price) * 2.00)
                msg = """[{}] [RSI ALERT] \n[{} {}]\nOverbought SHORT order
                {} entry price: {:.3f}$
                {} take-profit: {:.3f}$
                {} stop-loss:   {:.3f}$""".format(dt, TRADE_SYMBOL, TIMEFRAME, short, close_price, profit, profit_price, stop, stop_price)
                telegram_send.send(messages=[msg])

            if last_rsi < RSI_OVERSOLD:
                stop_price = close_price - (float(last_atr) * 2.00)
                profit_price = close_price + ((close_price-stop_price) * 2.00)
                msg = """[{}] [RSI ALERT] \n[{} {}]\nOversold LONG order
                {} entry price: {:.3f}$
                {} take-profit: {:.3f}$
                {} stop-loss:   {:.3f}$""".format(dt, TRADE_SYMBOL, TIMEFRAME, long, close_price, profit, profit_price, stop, stop_price)
                telegram_send.send(messages=[msg])
            
            # Defend from overflow
            closes.pop(0)
            highs.pop(0)
            lows.pop(0)


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
telegram_send.send(messages=[f'[{dt}] [SERVER] Crash server'])
