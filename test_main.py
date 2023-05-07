import http.client
import yfinance as yf
from supertrend import supertrend
from datetime import datetime
import main
import pandas as pd
import json
import numpy as np
import os

TEST_SYMBOL = "AAPL"
TEST_JSON_PATH ="./" + TEST_SYMBOL + ".json"
TEST_CSV_PATH = "./" + TEST_SYMBOL + ".csv"

def test_parse_args():
    args = main.parse_args("test_config.yaml")
    assert args != None
    assert args.symbol == "AAPL"
    assert args.atr_period != None
    assert args.atr_period == 3
    assert args.atr_multiplier != None
    assert args.atr_multiplier == 10

def test_download():
    df = main.download(TEST_SYMBOL, "1m")
    assert df.empty == False
    assert df.columns.size == 6

 
def test_save():
   df = main.download(TEST_SYMBOL, "1d", start_date='2023-01-01', end_date='2023-05-01')
   assert df.empty == False
   assert df.columns.size == 6

   main.save(TEST_SYMBOL, df)
   assert os.path.isfile(TEST_CSV_PATH) == True
   os.remove(TEST_CSV_PATH)

   main.save(TEST_SYMBOL, df, json=True)
   assert os.path.isfile("./AAPL.json")
   with open(TEST_JSON_PATH , mode='r+') as f:
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

   os.remove(TEST_JSON_PATH)
   assert os.path.isfile(TEST_JSON_PATH) == False

   #path = os.path.join(TEST_CSV_PATH)
   #df.to_csv(path_or_buf=path)

