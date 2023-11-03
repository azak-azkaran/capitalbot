import http.client
import yfinance as yf
from indicators import supertrend
from datetime import datetime
from main_module import main
from main_module import config
import pandas as pd
import json
import numpy as np
import os
import pytest
import requests
import mock_capital.mock_server as test_http_server

TEST_SYMBOL = "AAPL"
TEST_JSON_PATH = "./" + TEST_SYMBOL + ".json"
TEST_CSV_PATH = "./" + TEST_SYMBOL + ".csv"
TEST_CONFIG_PATH = "./tests/test_config.yaml"


@pytest.fixture()
def setup_mock(monkeypatch):
    # store a reference to the old get method
    monkeypatch.setattr(requests, "get", test_http_server.mocked_get)
    monkeypatch.setattr(requests, "post", test_http_server.mocked_get)



def test_download():
    df = main.download(TEST_SYMBOL, "1m")
    assert df.empty == False
    assert df.columns.size == 6


def test_main():
    main.main([TEST_CONFIG_PATH])

    assert os.path.isfile("./plots/foo.png")
    os.remove("./plots/foo.png")
    assert not os.path.isfile("./plots/foo.png")


def test_save():
    df = main.download(
        TEST_SYMBOL, "1d", start_date="2023-01-01", end_date="2023-05-01"
    )
    assert df.empty == False
    assert df.columns.size == 6

    main.save(TEST_SYMBOL, df)
    assert os.path.isfile(TEST_CSV_PATH) == True
    os.remove(TEST_CSV_PATH)

    main.save(TEST_SYMBOL, df, json=True)
    assert os.path.isfile("./AAPL.json")
    with open(TEST_JSON_PATH, mode="r+") as f:
        assert f is not None
        jsondata = json.load(f)

        assert jsondata is not None
        read_df = pd.DataFrame.from_dict(jsondata)
        assert read_df.columns.size == df.columns.size
        assert np.isclose(read_df.iloc[1, 1], df.iloc[1, 1])
        assert np.isclose(read_df.iloc[10, 1], df.iloc[10, 1])
        assert np.isclose(read_df.iloc[1, 5], df.iloc[1, 5])
        assert np.isclose(read_df.iloc[10, 5], df.iloc[10, 5])
        assert read_df.shape == df.shape

    os.remove(TEST_JSON_PATH)
    assert os.path.isfile(TEST_JSON_PATH) == False


def test_capitalize(setup_mock):
    if not os.path.exists("config.yaml"):
        print("No config file Probably Runner")
        args = config.Config(filename=TEST_CONFIG_PATH)
        args.capital_api_key = os.environ.get("CAPITAL_API_TOKEN")
        args.capital_identifier = os.environ.get("CAPITAL_IDENTIFIER")
        args.capital_password = os.environ.get("CAPITAL_PASSWORD")
    else:
        args = config.Config(filename="./config.yaml")
        args.symbol = "AAPL"
        args.filename = "foo.png"

    assert args.capital_api_key != None
    assert args.capital_api_key != ""
    assert args.dl_start != None
    assert args.dl_end != None

    df = main.capitalize(args)

    # supertrend_frame = main.mode_supertrend(df, args.atr_period, args.atr_multiplier)
    # df = df.join(supertrend_frame)

    main.plot_frame(df, "test.png")
    assert os.path.isdir("plots")
    assert os.path.isfile("./plots/test.png")
    os.remove("plots/test.png")
    assert not os.path.isfile("./plots/test.png")



def test_calculate_ema():
    df = main.download(TEST_SYMBOL, "1m")
    assert df.empty == False
    assert df.columns.size == 6
