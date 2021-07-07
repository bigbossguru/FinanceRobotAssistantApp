import websocket, json
import numpy as np
import talib
from talib import stream
import telegram_send, telegram
import datetime
from lib.exchange import Binance
import lib.config as conf
from lib.trade import Trade
# from pprint import pprint

# Telegram Bot 
bot = telegram.Bot(conf.API_TOKEN)

# Global constants
BALANCE = 1000.0
RSI_PERIOD = 14
ATR_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
RSI_MIDDLE = 50
TIMEFRAME = '1m'
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.05
SOCKET = f"wss://stream.binance.com:9443/ws/{TRADE_SYMBOL.lower()}@kline_{TIMEFRAME}"


def main():
    binance = Binance()
    trading = Trade(BALANCE)

    def on_open(ws):
        telegram_send.send(messages=[f'[{data_time_info()}] [SERVER] \nConnection is open'])

    def on_close(ws):
        telegram_send.send(messages=[f'[{data_time_info()}] [SERVER] \nConnection is close'])

    def on_message(ws, msg):
        json_msg = json.loads(msg)
        candlestick = json_msg['k']
        is_candle_closed = candlestick['x']
        open_price = float(candlestick['o'])
        close_price = float(candlestick['c'])
        high_price = float(candlestick['h'])
        low_price = float(candlestick['l'])

        if is_candle_closed:
            binance.record_candlesticks_data(open_price, close_price, high_price, low_price)
            data = binance.get_data()


            if len(data['candlestick']['close_prices']) > RSI_PERIOD:
                np_closes = np.array(data['candlestick']['close_prices'])
                np_highs = np.array(data['candlestick']['high_prices'])
                np_lows = np.array(data['candlestick']['low_prices'])
                rsi_ = stream.RSI(np_closes, timeperiod=14)
                atr_ = stream.ATR(np_highs, np_lows, np_closes, timeperiod=14)
                # rsi = talib.RSI(np_closes, timeperiod=RSI_PERIOD)
                # atr = talib.ATR(np_highs, np_lows, np_closes, timeperiod=ATR_PERIOD)
                last_rsi = rsi_[-1]
                last_atr = atr_[-1]
                binance.record_indicators_data(last_rsi, last_atr)
                # msg_bot = "{}\nclose price: {:.3f}\nlast_rsi: {:.1f}\nlast_atr: {:.1f}".format(data_time_info(), close_price, last_rsi, last_atr)
                # telegram_send.send(messages=[msg_bot])

                if last_rsi > RSI_OVERBOUGHT: 
                    stop_price = close_price + (float(last_atr) * 2.00)
                    profit_price = close_price - ((stop_price-close_price) * 2.00)
                    price_set = [close_price, profit_price, stop_price]
                    send_telegram_info(data_time_info(), price_set, 'RSI', 'SHORT', 'Overbought')
                    trading.order(TRADE_SYMBOL, TRADE_QUANTITY, close_price, stop_price, profit_price)
                    # print(price_set, last_rsi, last_atr)


                if last_rsi < RSI_OVERSOLD:
                    stop_price = close_price - (float(last_atr) * 2.00)
                    profit_price = close_price + ((close_price-stop_price) * 2.00)
                    price_set = [close_price, profit_price, stop_price]
                    send_telegram_info(data_time_info(), price_set, 'RSI', 'LONG', 'Oversold')
                    trading.order(TRADE_SYMBOL, TRADE_QUANTITY, close_price, stop_price, profit_price)
                    # print(price_set, last_rsi, last_atr)
        
        trading.update_market(close_price)


    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()
    telegram_send.send(messages=[f'[{data_time_info()}] [SERVER] Closed server'])

def data_time_info():
    dt = datetime.datetime.now()
    dt = dt.strftime("%d.%m|%H:%M")
    return dt

def send_telegram_info(d_t, prices, indicator='N/A', type_pos='N/A', level_type='N/A'):
    long = '↗️'
    short = '↘️'
    stop = '⏹'
    profit = '🆗'
    test = '*⃣'

    if type_pos.upper() == "SHORT": dir_pos = short
    elif type_pos.upper() == "LONG": dir_pos = long
    else: dir_pos = test

    msg = """[{}] [{} ALERT] \n[{} {}]\n{} {} order
    {} entry price: {:.3f}$
    {} take-profit: {:.3f}$
    {} stop-loss:   {:.3f}$""".format(d_t, indicator, TRADE_SYMBOL, TIMEFRAME, level_type, type_pos, dir_pos, prices[0], profit, prices[1], stop, prices[2])
    bot.send_message(chat_id=conf.ID_GROUP, text=msg)


if __name__ == "__main__":
    main()