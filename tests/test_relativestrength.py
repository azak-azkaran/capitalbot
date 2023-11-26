import http.client
import numpy as np
import pandas as pd
import yfinance as yf
import os
from main_module import main
from indicators import relativestrength
from indicators import supertrend


def test_relative_strength_index():
    foo_filename = "./foo.png"
    if os.path.exists(foo_filename):
        os.remove(foo_filename)

    df = yf.download("AAPL", start="2023-01-01", end="2023-11-09", interval="1h")
    assert df.empty == False

    close = df["Close"].to_numpy()
    rsi, indicator, long, short, sma = relativestrength.relative_strength_index(close)
    entry, exit, roi, earning = supertrend.backtest(
        close,
        indicator,
        investment=10000,
        debug=False,
        commission=0,
    )

    main.plot_frame(
        df,
        foo_filename,
        pd.Series(entry, index=df.index),
        pd.Series(exit, index=df.index),
    )
