import pandas as pd
import numpy as np
from datetime import datetime
import math
import backtrader as bt
import talib
from numba import njit


# Create a Stratey
class SuperTrendStrategy(bt.Strategy):
    params = (("period", 7), ("dolog", False), ("multiplier", 3))

    def __init__(self):
        self.x = SuperTrend(
            self.data, period=self.p.period, multiplier=self.p.multiplier
        )
        self.dclose = self.datas[0].close
        self.cross = bt.ind.CrossOver(self.dclose, self.x)
        self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

    def log(self, txt, dt=None, doprint=False):
        """Logging function fot this strategy"""
        if self.params.dolog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(dt.isoformat() + " , " + txt)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Size %.2f"
                    % (order.executed.price, order.executed.value, order.executed.size)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Size %.2f"
                    % (order.executed.price, order.executed.value, order.executed.size)
                )
            self.bar_executed = len(self)

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log(
            "Close, %.2f - SuperTrend: %.2f"
            % (
                self.dataclose[0],
                self.x[0],
            )
        )
        pos = self.getposition(self.data)
        dpos = pos.size
        if self.cross[0] == 1 and dpos <= 0:
            self.order_target_percent(data=self.data, target=1)
        elif self.cross[0] == -1 and dpos >= 0:
            self.order_target_percent(data=self.data, target=-1)

    def stop(self):
        self.log(
            "(SuperTrend Period %2d, Multiplier %2d) Ending Value %.2f"
            % (self.params.period, self.params.multiplier, self.broker.getvalue()),
            doprint=True,
        )


class SuperTrend(bt.Indicator):
    """
    SuperTrend Algorithm :
    BASIC UPPERBAND = (high + low) / 2 + Multiplier * ATR
    BASIC lowERBAND = (high + low) / 2 - Multiplier * ATR

    FINAL UPPERBAND = IF( (Current BASICUPPERBAND < Previous FINAL UPPERBAND) or (Previous close > Previous FINAL UPPERBAND))
        THEN (Current BASIC UPPERBAND) ELSE Previous FINALUPPERBAND)

    FINAL lowERBAND = IF( (Current BASIC lowERBAND > Previous FINAL lowERBAND) or (Previous close < Previous FINAL lowERBAND))
        THEN (Current BASIC lowERBAND) ELSE Previous FINAL lowERBAND)
    SUPERTREND = IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current close <= Current FINAL UPPERBAND))
        THEN Current FINAL UPPERBAND
    ELSE
        IF((Previous SUPERTREND = Previous FINAL UPPERBAND) and (Current close > Current FINAL UPPERBAND))
            THEN Current FINAL lowERBAND
        ELSE
            IF((Previous SUPERTREND = Previous FINAL lowERBAND) and (Current close >= Current FINAL lowERBAND))
                THEN Current FINAL lowERBAND
            ELSE
                IF((Previous SUPERTREND = Previous FINAL lowERBAND) and (Current close < Current FINAL lowERBAND))
                    THEN Current FINAL UPPERBAND
    """

    lines = ("super_trend", "f_lowerband", "f_upperband")
    params = (
        ("period", 7),
        ("multiplier", 3),
    )
    plotlines = dict(
        super_trend=dict(_name="ST", color="blue", alpha=0),
        f_lowerband=dict(_name="f_lowerband", color="green", alpha=1),
        f_upperband=dict(_name="f_lowerband", color="red", alpha=1),
    )

    plotinfo = dict(subplot=False)

    def __init__(self):
        self.st = [0]
        self.finalupband = [0]
        self.finallowband = [0]
        self.addminperiod(self.p.period)
        atr = bt.ind.ATR(self.data, period=self.p.period)
        self.upperband = (self.data.high + self.data.low) / 2 + self.p.multiplier * atr
        self.lowerband = (self.data.high + self.data.low) / 2 - self.p.multiplier * atr

    def next(self):
        pre_upband = self.finalupband[0]
        pre_lowband = self.finallowband[0]

        if (
            self.upperband[0] < self.finalupband[-1]
            or self.data.close[-1] > self.finalupband[-1]
        ):
            self.finalupband[0] = self.upperband[0]

        else:
            self.finalupband[0] = self.finalupband[-1]

        if (
            self.lowerband[0] > self.finallowband[-1]
            or self.data.close[-1] < self.finallowband[-1]
        ):
            self.finallowband[0] = self.lowerband[0]

        else:
            self.finallowband[0] = self.finallowband[-1]

        if self.data.close[0] <= self.finalupband[0] and ((self.st[-1] == pre_upband)):
            self.st[0] = self.finalupband[0]
            self.lines.super_trend[0] = self.finalupband[0]
            self.lines.f_upperband[0] = self.finalupband[0]

        elif (self.st[-1] == pre_upband) and (self.data.close[0] > self.finalupband[0]):
            self.st[0] = self.finallowband[0]
            self.lines.super_trend[0] = self.finallowband[0]
            self.lines.f_lowerband[0] = self.finallowband[0]

        elif (self.st[-1] == pre_lowband) and (
            self.data.close[0] >= self.finallowband[0]
        ):
            self.st[0] = self.finallowband[0]
            self.lines.super_trend[0] = self.finallowband[0]
            self.lines.f_lowerband[0] = self.finallowband[0]

        elif (self.st[-1] == pre_lowband) and (
            self.data.close[0] < self.finallowband[0]
        ):
            self.st[0] = self.finalupband[0]
            self.lines.super_trend[0] = self.st[0]
            # self.lines.f_upperband[0] = self.st[0]

@njit
def get_basic_bands(med_price, atr, multiplier):
    matr = multiplier * atr
    upper = med_price + matr
    lower = med_price - matr
    return upper, lower

@njit
def get_final_bands_nb(close, upper, lower):
    trend = np.full(close.shape, np.nan)
    dir_ = np.full(close.shape, 1)
    long = np.full(close.shape, np.nan)
    short = np.full(close.shape, np.nan)

    for i in range(1, close.shape[0]):
        if close[i] > upper[i - 1]:
            dir_[i] = 1
        elif close[i] < lower[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lower[i] < lower[i - 1]:
                lower[i] = lower[i - 1]
            if dir_[i] < 0 and upper[i] > upper[i - 1]:
                upper[i] = upper[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lower[i]
        else:
            trend[i] = short[i] = upper[i]
            
    return trend, dir_, long, short

def faster_supertrend_talib(high, low, close, period=7, multiplier=3):
    avg_price = talib.MEDPRICE(high, low)
    atr = talib.ATR(high, low, close, period)
    upper, lower = get_basic_bands(avg_price, atr, multiplier)
    return get_final_bands_nb(close, upper, lower)

def supertrend_opt(high, low, close, period=7, multiplier=3):
    supert = np.full(close.shape, np.nan)
    superd = np.full(close.shape, np.nan)
    superl = np.full(close.shape, np.nan)
    supers = np.full(close.shape, np.nan)
    for x in range(close.shape[1]):
        t, d, l,s = faster_supertrend_talib(high[x], low[x], close[x], period, multiplier)
        supert[x] = t
        superd[x] = d 
        superl[x] = l
        supers[x] = s
    
    return supert, superd, superl, supers

def get_indicator(high, low, close, period=7, multiplier=3):
    indicator = np.full(close.shape, np.nan)
    supert, _, superl, supers = faster_supertrend_talib(low=low, high=high, close=close, period=period, multiplier=multiplier)
    indicator = np.where(supert == supers, False, np.where(supert == superl, True, np.nan))
    return indicator, superl, supers

def supertrend(df, atr_period, multiplier):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    # initialize Supertrend column to True
    supert, _, superl, supers = faster_supertrend_talib(low=low.to_numpy(), high=high.to_numpy(), close=close.to_numpy(), period=atr_period, multiplier=multiplier)
    st = pd.Series(np.where(supert == supers, False, np.where(supert == superl, True, np.nan)), index = close.index)

    return pd.DataFrame(
        {
            "Supertrend": st,
            "Final Lowerband": superl,
            "Final Upperband": supers,
        },
        index=df.index,
    )


@njit
def backtest(close, indicator, investment, debug=False, commission=5):

    entry = np.full(close.shape, np.nan)
    exit = np.full(close.shape, np.nan)
    # initial condition
    in_position = False
    equity = investment
    share = 0

    for i in range(1, close.shape[0]):
        # if not in position & price is on uptrend -> buy

        if not in_position and indicator[i]:
            share = math.floor(equity / close[i])
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            equity -= share * close[i]
            entry[i] =close[i]
            in_position = True
            #if debug:
            #    print(
            #        f'Buy {share} shares at {round(close[i],2)} on {df.index[i].strftime("%Y/%m/%d")}'
            #    )
        # if in position & price is not on uptrend -> sell
        elif in_position and not indicator[i]:
            equity += share * close[i] - commission
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            exit[i] = close[i]
            in_position = False
            #if debug:
            #    print(
            #        f'Sell at {round(close.iloc[i],2)} on {df.index[i].strftime("%Y/%m/%d")}'
            #    )
    # if still in position -> sell all share
    if in_position:
        equity += share * close[i] - commission

    earning = equity - investment
    roi = round(earning / investment * 100, 2)
    #if debug:
    #    print(
    #        f"Earning from investing ${investment} is ${round(earning,2)} (ROI = {roi}%)"
    #    )
    return entry, exit, roi, earning


# BONUS: parameter optimization
def find_optimal_parameter(
    high, low, close,
    investment=10000,
    atr_period=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    atr_multiplier=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0],
):
    roi_list = np.zeros(( len(atr_multiplier) * len(atr_period),3 ))

    # for each period and multiplier, perform backtest
    i = 0
    for period, multiplier in [(x, y) for x in atr_period for y in atr_multiplier]:
        roi_list[i][0] = period
        roi_list[i][1] = multiplier
        indicator, _, _ = get_indicator(close=close, high=high, low=low, period=period, multiplier=multiplier)
        _, _, roi,_ = backtest(close=close, indicator=indicator, investment=investment)
        #roi_list.append((period, multiplier, roi))
        roi_list[i][2] = roi
        i+=1


    #print(pd.DataFrame(roi_list, columns=["ATR_period", "Multiplier", "ROI"]))

    return roi_list
    # return the best parameter set
    #return max(roi_list, key=lambda x: x[2])
