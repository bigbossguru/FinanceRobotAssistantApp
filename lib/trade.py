from math import fabs
import os
# from random import randrange
import uuid, csv
import datetime

class Trade:
    _id_transaction = None
    _date_time_trans = None
    _clean_price = 0.0

    def __init__(self, balance):
        self._balance = balance
        self._in_position = False
    
    def order(self, symbol: str, lot: float, entry_price: float, loss_price: float, profit_price: float, dir_order=None):
        if not self._in_position:
            self._lot = lot
            self._symbol = symbol
            self._entry_price = entry_price
            self._loss_price = loss_price
            self._profit_price = profit_price
            return False
        else:
            print('You are in position\n'.upper())
            return True

    def get_info(self):
        print(f"Balance: {self._balance} $\nIn position: {self._in_position}\nID Transation: {self._id_transaction}\nClean price: {self._clean_price} $\nDate and Time Trans: {self._date_time_trans}\n")

    def _save_in_file(self):
        header = ('id_transaction','date_time','symbol','balance','lot','entry_price','stop_loss_price','take_profit_price','clean_price')
        row = (self._id_transaction,self._date_time_trans,self._symbol,round(self._balance, 3),self._lot,self._entry_price,round(self._loss_price, 3),round(self._profit_price, 3),round(self._clean_price, 3))
        if not os.path.exists("data.csv"):
            with open("data.csv", "w", newline='') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(header)
                f_csv.writerow(row)
        else:
            with open("data.csv", "a", newline='') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(row)

    def _balance_calculate(self, loss=False, profit=False):
        if loss or profit:
            _tmp_balance = self._balance
            self._in_position = False
            if loss:
                self._balance -= (fabs(self._entry_price - self._loss_price)) * self._lot
            elif profit:
                self._balance += (fabs(self._entry_price - self._loss_price)) * self._lot
            else: pass
            self._clean_price = self._balance - _tmp_balance
            self._save_in_file()
            self._id_transaction = None
            self._date_time_trans = None
        else:
            return

    def update_market(self, close_price: float):        
        if not self._in_position and (close_price == self._entry_price):
            self._in_position = True
            self._date_time_trans = str(datetime.datetime.now())
            self._id_transaction = str(uuid.uuid1())
            self._clean_price = 0.0
        else:
            if self._in_position:
                if self._profit_price < self._entry_price < self._loss_price:
                    if close_price >= self._loss_price:
                        self._balance_calculate(loss=True)
                    if close_price <= self._profit_price:
                        self._balance_calculate(profit=True)
                
                if self._profit_price > self._entry_price > self._loss_price:
                    if close_price <= self._loss_price:
                        self._balance_calculate(loss=True)
                    if close_price >= self._profit_price:
                        self._balance_calculate(profit=True)
