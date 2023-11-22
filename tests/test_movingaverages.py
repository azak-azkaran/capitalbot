import http.client
import yfinance as yf
import os
import numpy as np
from datetime import datetime, timedelta
from indicators import movingaverages
import matplotlib.pyplot as plt
from main_module import main


def test_ema():
    df = yf.download("AAPL", period="1d", interval="5m")
    assert df.empty is False

    ema = movingaverages.calculate_ema(df)
    assert ema.empty is False

    ema = movingaverages.calculate_ema(df, span=20, location=3)
    assert ema.empty is False
    print(df)


def test_sma():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty is False

    sma = movingaverages.calculate_sma(df)
    assert sma.empty is False

    sma = movingaverages.calculate_sma(df, location=3, smoothing=3)
    assert sma.empty is False
    print(df)


def test_cma():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty is False

    cma = movingaverages.calculate_cma(df)
    assert cma.empty is False

    cma = movingaverages.calculate_cma(df, period=5, location=3)
    assert cma.empty is False
    print(df)


def test_calculate_trend():
    foo_filename = "./foo.png"
    if os.path.exists(foo_filename):
        os.remove(foo_filename)

    df = yf.download("AAPL", period="1d", interval="5m")
    assert df.empty is False

    ema = movingaverages.calculate_ema(df, location=3)
    assert ema.empty is False

    df = movingaverages.calculate_trend(df, ema)
    print(df)

    filename = "plots/" + foo_filename
    plt.figure(figsize=(16, 9), dpi=360)
    plt.plot(df["Close"], label="Close Price")
    plt.plot(df["EMA"], label="EMA Price")

    for index, row in df.iterrows():
        print("index: ", index, " EMA: ", row["EMA"], " Close: ", row["Close"])
        if row["EMA"] is np.nan:
            continue
        if row["EMA"]:
            plt.plot(
                index,
                row["Close"],
                marker="^",
                color="green",
                markersize=12,
                linewidth=0,
                label="Entry",
            )
        if not row["EMA"]:
            plt.plot(
                index,
                row["Close"],
                marker="v",
                color="red",
                markersize=12,
                linewidth=0,
                label="Exit",
            )

    plt.savefig(filename)

