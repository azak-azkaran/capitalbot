import http.client
import yfinance as yf
from supertrend import supertrend
from datetime import datetime
import main
import pandas as pd
import json
import numpy as np
import os

def test_parse_args():
    args = main.parse_args("test_config.yaml")
    assert args != None
    assert args.symbol == "AAPL"
    assert args.atr_period != None
    assert args.atr_period == 3
    assert args.atr_multiplier != None
    assert args.atr_multiplier == 10

def test_download():
    df = main.download("AAPL", "1m")
    assert df.empty == False
    assert df.columns.size == 6

    df = main.download("AAPL", "1d", save_to_file=True, start_date='2023-01-01', end_date='2023-05-01')
    assert df.empty == False
    assert df.columns.size == 6

    with open("./AAPL.json" , mode='r+') as f:
        assert f is not None
        jsondata =json.load(f)

        assert jsondata is not None
        read_df = pd.DataFrame.from_dict(jsondata)
        assert read_df.columns.size == df.columns.size
        assert np.isclose(read_df.iloc[1,1], df.iloc[1,1])
        assert np.isclose(read_df.iloc[10,1], df.iloc[10,1])
        assert np.isclose(read_df.iloc[1,5], df.iloc[1,5])
        assert np.isclose(read_df.iloc[10,5], df.iloc[10,5])
        assert read_df.shape == df.shape

    assert os.path.isfile("./AAPL.json")
    os.remove("./AAPL.json")
    assert os.path.isfile("./AAPL.json") == False