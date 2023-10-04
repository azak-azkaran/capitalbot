import pandas as pd
import numpy as np


def calculate_sma(prices, smoothing=2, location=0):
    name = "SMA_" + prices.columns[location]
    prices[name] = prices.iloc[:, location].rolling(window=smoothing).mean()
    return prices


def calculate_cma(prices, period=4, location=0):
    name = "CMA_" + prices.columns[location]
    prices[name] = prices.iloc[:, location].expanding(min_periods=period).mean()
    return prices


def calculate_ema(prices, span=10, location=0, adjust=False):
    name = "EMA_" + prices.columns[location]

    ema = prices.iloc[:, location].ewm(span=span, adjust=adjust).mean()
    prices[name] = ema
    return prices
