import pandas as pd
import numpy as np
import talib


def relative_strength_index(close, period=14, overbought=70, oversold=30):
    long = np.full(close.shape, np.nan)
    short = np.full(close.shape, np.nan)
    indicator = np.full(close.shape, np.nan)
    rsi = talib.RSI(close, timeperiod=period)
    for i in range(1, close.shape[0]):
        if rsi[i] > overbought:
            long[i] = close[i]
            indicator[i] = True
        if rsi[i] < oversold:
            short[i] = close[i]
            indicator[i] = False
    sma = talib.SMA(rsi)
    return rsi, indicator, long, short, sma
    # return trend, dir_, long, short
    # np.where(supert == supers, False, np.where(supert == superl, True, np.nan)),
