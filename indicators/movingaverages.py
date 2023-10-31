import pandas as pd
import numpy as np
import backtrader as bt


# Create a Stratey
class EMAStrategy(bt.Strategy):
    params = (
        ("period", 20),
        ("dolog", False),
    )

    def __init__(self):
        self.sma = bt.talib.EMA(self.data, timeperiod=self.p.period)
        # Keep a reference to the "close" line in the data[0] dataseries
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

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log("Close, %.2f" % self.dataclose[0])

        ## Check if we are in the market
        # if not self.position:
        # Not yet ... we MIGHT BUY if ...
        if self.data.close[0] > self.sma[0]:
            # BUY, BUY, BUY!!! (with default parameters)
            self.log("BUY CREATE, %.2f" % self.dataclose[0])
            self.order = self.buy()

        if self.data.close[0] < self.sma[0]:
            # SELL, SELL, SELL!!! (with all possible default parameters)
            self.log("SELL CREATE, %.2f" % self.dataclose[0])
            self.order = self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log("BUY EXECUTED, %.2f" % order.executed.price)
            elif order.issell():
                self.log("SELL EXECUTED, %.2f" % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        # Write down: no pending order
        self.order = None

    def stop(self):
        self.log(
            "(MA Period %2d) Ending Value %.2f"
            % (self.params.period, self.broker.getvalue()),
            doprint=True,
        )


def _calc(x):
    if x > 0.1:
        return True
    if x < -0.1:
        return False
    else:
        return np.nan


def calculate_sma(prices, smoothing=2, location=0):
    name = "SMA_" + prices.columns[location]
    sma = prices.iloc[:, location].rolling(window=smoothing).mean()
    sma.name = name
    return sma


def calculate_cma(prices, period=4, location=0):
    name = "CMA_" + prices.columns[location]
    cma = prices.iloc[:, location].expanding(min_periods=period).mean()
    return cma


def calculate_ema(prices, span=10, location=0, adjust=False):
    name = "EMA_" + prices.columns[location]

    ema = prices.iloc[:, location].ewm(span=span, adjust=adjust).mean()
    ema.name = name
    return ema


def calculate_trend(df, ma):
    close = df["Close"]
    # calculate ATR
    price_diffs = close - ma
    trend = price_diffs.apply(_calc)
    df["EMA"] = ma
    df["Trend"] = trend
    return df
