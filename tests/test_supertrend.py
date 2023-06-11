import http.client
import yfinance as yf
import os
from supertrend import supertrend
from supertrend import backtest_supertrend
from supertrend import find_optimal_parameter
from datetime import datetime
from main import plot_frame


def test_supertrend():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty == False
    print(df)
    st = supertrend(df, 5, 10)
    assert st.empty == False

    print(st)
    assert st.columns.size == 3
    assert st.index.size >= 1


def test_backtest_supertrend():
    if os.path.exists("./foo.png"):
        os.remove("./foo.png")

    atr_period = 7
    atr_multiplier = 3

    stock_list = ["AAPL"]
    for symbol in stock_list:
        df = yf.download("AAPL", start="2023-06-05", end="2023-06-10", interval="5m")
        st = supertrend(df, atr_period, atr_multiplier)
        df = df.join(st)

    # df.tail(15)
    entry, exit, roi = backtest_supertrend(df, 10000, debug=True)
    assert len(entry) != 0
    assert len(exit) != 0

    plot_frame(df, "./foo.png", entry, exit)
    assert os.path.exists("./foo.png")


def test_find_optimal_parameter():
    df = yf.download("AAPL", start="2023-06-05", end="2023-06-09", interval="5m")
    optimal_param = find_optimal_parameter(df)
    print(
        f"Best parameter set: ATR Period={optimal_param[0]}, Multiplier={optimal_param[1]}, ROI={optimal_param[2]}"
    )
