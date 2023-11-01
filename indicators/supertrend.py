import pandas as pd
import numpy as np
from datetime import datetime
import math
import backtrader as bt


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
        if self.cross[0]==1 and dpos <= 0:
            self.order_target_percent(data=self.data, target=1)
        elif self.cross[0]==-1 and dpos >= 0:
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

    lines = ("super_trend","f_lowerband", "f_upperband")
    params = (
        ("period", 7),
        ("multiplier", 3),
    )
    plotlines = dict(super_trend=dict(_name="ST", color="blue", alpha=0),
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
            #self.lines.f_upperband[0] = self.st[0]



def supertrend(df, atr_period, multiplier):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    # calculate ATR
    price_diffs = [high - low, high - close.shift(), close.shift() - low]
    true_range = pd.concat(price_diffs, axis=1)
    true_range = true_range.abs().max(axis=1)
    # default ATR calculation in supertrend indicator
    atr = true_range.ewm(alpha=1 / atr_period, min_periods=atr_period).mean()

    # HL2 is simply the average of high and low prices
    hl2 = (high + low) / 2
    # upperband and lowerband calculation
    # notice that final bands are set to be equal to the respective bands
    final_upperband = hl2 + (multiplier * atr)
    final_lowerband = hl2 - (multiplier * atr)

    # initialize Supertrend column to True
    supertrend = [True] * len(df)

    for i in range(1, len(df.index)):
        curr, prev = i, i - 1

        # if current close price crosses above upperband
        if close.iloc[curr] > final_upperband.iloc[prev]:
            supertrend[curr] = True
        # if current close price crosses below lowerband
        elif close.iloc[curr] < final_lowerband.iloc[prev]:
            supertrend[curr] = False
        # else, the trend continues
        else:
            supertrend[curr] = supertrend[prev]

            # adjustment to the final bands
            if (
                supertrend[curr] is True
                and final_lowerband.iloc[curr] < final_lowerband.iloc[prev]
            ):
                final_lowerband.iloc[curr] = final_lowerband.iloc[prev]
            if (
                supertrend[curr] is False
                and final_upperband.iloc[curr] > final_upperband.iloc[prev]
            ):
                final_upperband.iloc[curr] = final_upperband.iloc[prev]

        # to remove bands according to the trend direction
        if supertrend[curr] is True:
            final_upperband.iloc[curr] = np.nan
        else:
            final_lowerband.iloc[curr] = np.nan

    return pd.DataFrame(
        {
            "Supertrend": supertrend,
            "Final Lowerband": final_lowerband,
            "Final Upperband": final_upperband,
        },
        index=df.index,
    )


def backtest_supertrend(df, investment, debug=False, commission=5):
    is_uptrend = df["Supertrend"]
    close = df["Close"]

    # initial condition
    in_position = False
    equity = investment
    share = 0
    entry = []
    exit = []

    df.to_csv("test.csv")

    for i in range(2, len(df)):
        # if not in position & price is on uptrend -> buy

        if not in_position and is_uptrend.iloc[i]:
            share = math.floor(equity / close.iloc[i])
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            equity -= share * close.iloc[i]
            entry.append((i, close.iloc[i]))
            in_position = True
            if debug:
                print(
                    f'Buy {share} shares at {round(close.iloc[i],2)} on {df.index[i].strftime("%Y/%m/%d")}'
                )
        # if in position & price is not on uptrend -> sell
        elif in_position and not is_uptrend.iloc[i]:
            equity += share * close.iloc[i] - commission
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            exit.append((i, close.iloc[i]))
            in_position = False
            if debug:
                print(
                    f'Sell at {round(close.iloc[i],2)} on {df.index[i].strftime("%Y/%m/%d")}'
                )
    # if still in position -> sell all share
    if in_position:
        equity += share * close.iloc[i] - commission

    earning = equity - investment
    roi = round(earning / investment * 100, 2)
    if debug:
        print(
            f"Earning from investing ${investment} is ${round(earning,2)} (ROI = {roi}%)"
        )
    return entry, exit, roi


# BONUS: parameter optimization
def find_optimal_parameter(
    df,
    investment=10000,
    atr_period=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    atr_multiplier=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0],
):
    roi_list = []

    # for each period and multiplier, perform backtest
    for period, multiplier in [(x, y) for x in atr_period for y in atr_multiplier]:
        new_df = df
        st = supertrend(df, period, multiplier)
        new_df = df.join(st)
        new_df = new_df[period:]
        _, _, roi = backtest_supertrend(new_df, investment)
        roi_list.append((period, multiplier, roi))

    print(pd.DataFrame(roi_list, columns=["ATR_period", "Multiplier", "ROI"]))

    # return the best parameter set
    return max(roi_list, key=lambda x: x[2])
