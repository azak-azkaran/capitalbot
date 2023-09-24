import http.client
import yfinance as yf
import os
from supertrend import supertrend
from supertrend import backtest_supertrend
from supertrend import find_optimal_parameter
from datetime import datetime, timedelta
from main import plot_frame
import movingaverages
import matplotlib.pyplot as plt


def test_sma():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty == False

    df = movingaverages.calculate_sma(df)
    assert df["SMA_Open"].empty == False

    df = movingaverages.calculate_sma(df, location=3, smoothing=3 )
    assert df["SMA_Close"].empty == False
    print(df)

def test_cma():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty == False

    df = movingaverages.calculate_cma(df)
    assert df["CMA_Open"].empty == False

    df = movingaverages.calculate_cma(df, period=5, location=3 )
    assert df["CMA_Close"].empty == False
    print(df)

