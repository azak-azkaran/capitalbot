import http.client
import yfinance as yf
import os
from indicators import supertrend
from datetime import datetime, timedelta
from main_module import main


def test_supertrend():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty == False
    print(df)
    st = supertrend.supertrend(df, 5, 10)
    assert st.empty == False

    print(st)
    assert st.columns.size == 3
    assert st.index.size >= 1


def test_backtest_supertrend():
    foo_filename = "./foo.png"
    if os.path.exists(foo_filename):
        os.remove(foo_filename)

    atr_period = 7
    atr_multiplier = 3

    stock_list = ["AAPL"]
    for symbol in stock_list:
        date = datetime.now() - timedelta(days=1)
        start_date = date - timedelta(days=5)

        df = yf.download(
            symbol,
            start=start_date.strftime("%Y-%m-%d"),
            end=date.strftime("%Y-%m-%d"),
            interval="5m",
        )
        st = supertrend.supertrend(df, atr_period, atr_multiplier)
        df = df.join(st)

    # df.tail(15)
    entry, exit, roi = supertrend.backtest_supertrend(df, 10000, debug=True)
    assert len(entry) != 0
    assert len(exit) != 0

    main.plot_frame(df, foo_filename, entry, exit)
    assert os.path.exists("plots/" + foo_filename)


def test_find_optimal_parameter():
    df = yf.download("AAPL", start="2023-06-05", end="2023-06-09", interval="5m")
    optimal_param = supertrend.find_optimal_parameter(df)
    print(
        f"Best parameter set: ATR Period={optimal_param[0]}, Multiplier={optimal_param[1]}, ROI={optimal_param[2]}"
    )
