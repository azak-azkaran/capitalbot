import http.client
import yfinance as yf
import os
from datetime import datetime, timedelta
from indicators import movingaverages
import matplotlib.pyplot as plt


def test_ema():
    df = yf.download("AAPL", period="1d", interval="5m")
    assert df.empty is False

    df = movingaverages.calculate_ema(df)
    assert df["EMA_Open"].empty is False

    df = movingaverages.calculate_ema(df, span=20, location=3)
    assert df["EMA_Close"].empty is False
    print(df)


def test_sma():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty is False

    df = movingaverages.calculate_sma(df)
    assert df["SMA_Open"].empty is False

    df = movingaverages.calculate_sma(df, location=3, smoothing=3)
    assert df["SMA_Close"].empty is False
    print(df)


def test_cma():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty is False

    df = movingaverages.calculate_cma(df)
    assert df["CMA_Open"].empty is False

    df = movingaverages.calculate_cma(df, period=5, location=3)
    assert df["CMA_Close"].empty is False
    print(df)
