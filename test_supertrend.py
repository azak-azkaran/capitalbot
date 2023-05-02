import http.client
import yfinance as yf
from supertrend import supertrend
from datetime import datetime


def test_supertrend():
    df = yf.download("AAPL", period="1d",interval="1h")
    assert df.empty == False
    print(df)
    st = supertrend(df, 5, 10)
    assert st.empty == False

    print(st)
    assert st.columns.size == 3
    assert st.index.size >= 1