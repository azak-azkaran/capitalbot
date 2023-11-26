import pandas as pd
import numpy as np


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
