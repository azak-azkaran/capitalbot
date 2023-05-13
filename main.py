import argparse
from supertrend import supertrend
import yfinance as yf
import matplotlib.pyplot as plt
import yaml
import sys
import os
import capital
import pandas as pd


from datetime import datetime, timezone, timedelta



class Config:
    symbol = ""
    atr_period = 0
    atr_multiplier = 0
    dl_period = ""
    dl_interval = ""
    dl_start = None
    dl_end = None
    capital_api_key = ""
    capital_password = ""
    capital_identifier = ""


def parse_args(filename):
    with open(filename, "r") as file:
        conf = yaml.safe_load(file)

        args = Config()
        args.symbol = conf.get("symbol")
        if conf.get("atr") == None:
            raise ValueError("atr must be specified")

        args.atr_period = conf.get("atr").get("period")
        if args.atr_period == None:
            raise ValueError("atr.period must be specified")
        args.atr_multiplier = conf.get("atr").get("multiplier")
        if args.atr_multiplier == None:
            raise ValueError("atr.multiplier must be specified")

        if conf.get("capital") != None:
            args.capital_api_key = conf.get("capital").get("api_key")
            args.capital_password = conf.get("capital").get("password")
            args.capital_identifier = conf.get("capital").get("identifier")

    return args


def download(symbol, interval, period="max", start_date=None, end_date=None):
    df = yf.download(
        tickers=symbol, period=period, interval=interval, start=start_date, end=end_date
    )
    return df


def save(symbol, df, json=False):
    if json:
        path = os.path.join("./" + symbol + ".json")
        df.to_json(path_or_buf=path)
    else:
        path = os.path.join("./" + symbol + ".csv")
        df.to_csv(path_or_buf=path)


def main(argv):
    """
    main
    """
    args = parse_args(argv[0])
    df = download(args.symbol, "5d", "1m")
    print(df)
    supertrend_frame = supertrend(df, args.atr_period, args.atr_multiplier)

    print(supertrend_frame)
    df = df.join(supertrend_frame)
    plot_frame(df, "foo.png")


def plot_frame(df, filename):
    plt.plot(df["Close"], label="Close Price")
    plt.plot(df["Final Lowerband"], "g", label="Final Lowerband")
    plt.plot(df["Final Upperband"], "r", label="Final Upperband")
    plt.savefig(filename)


def capitalize(config):
    if (
        config.capital_api_key == None
        or config.capital_password == None
        or config.capital_identifier == None
    ):
        raise ValueError("Please provide capital_api_key and capital_password")

    _, _, security, cst = capital.create_session(
        config.capital_api_key,
        config.capital_password,
        config.capital_identifier,
        demo=True,
    )

    date = datetime.now().replace(second=0)
    start_date = (date - timedelta(days=3, hours=2)).strftime(capital.CAPITAL_STRING_FORMAT)
    end_date = (date - timedelta(hours=2)).strftime(capital.CAPITAL_STRING_FORMAT)

    df = capital.download(
        config.symbol,
        security,
        cst,
        "MINUTE_5",
        start_date=start_date,
        end_date=end_date,
    )
    if df is None:
        raise ValueError("No download")

    changed = df.loc[
        :,
        [
            "openPrice.ask",
            "highPrice.ask",
            "lowPrice.ask",
            "closePrice.ask",
            "lastTradedVolume",
        ],
    ]
    changed = changed.rename(
        columns={
            "openPrice.ask": "Open",
            "highPrice.ask": "High",
            "lowPrice.ask": "Low",
            "closePrice.ask": "Close",
            "lastTradedVolume": "Volume",
        }
    )
    sf = supertrend(changed, config.atr_period, config.atr_multiplier)
    df = changed.join(sf)
    df.index = pd.to_datetime(df.index, format="%Y-%m-%dT%H:%M:%S")

    return df


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
