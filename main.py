import argparse
import yfinance as yf
from supertrend import supertrend
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
    capital_security_token = ""
    capital_cst_token = ""
    demo = True


def parse_period(period):
    # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y
    days = 0
    months = 0
    years = 0
    if period == "1d":
        days = 1
    elif period == "5d":
        days = 5
    elif period == "1mo":
        months = 1
    elif period == "3mo":
        months = 3
    elif period == "6mo":
        months = 6
    elif period == "1y":
        years = 1
    elif period == "2y":
        years = 2
    elif period == "5y":
        years = 5
    elif period == "10y":
        years = 10
    else:
        raise ValueError(
            "Period is not equviliant to: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y"
        )

    date = datetime.now()
    start_date = date - timedelta(days=days)

    if months > 0:
        start_date = start_date.month - months

    if years > 0:
        start_date = start_date.year - years

    end_date = date - timedelta(hours=2)
    return start_date, end_date


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

        if conf.get("period") != None:
            start, end = parse_period(conf.get("period"))
            args.dl_start = start
            args.dl_end = end

        if conf.get("start") != None:
            args.dl_start = conf.get("start")

        if conf.get("end") != None:
            args.dl_end = conf.get("end")

    return args


def save(symbol, df, json=False):
    if json:
        path = os.path.join("./" + symbol + ".json")
        df.to_json(path_or_buf=path)
    else:
        path = os.path.join("./" + symbol + ".csv")
        df.to_csv(path_or_buf=path)


def download(symbol, interval, period="max", start_date=None, end_date=None):
    df = yf.download(
        tickers=symbol, period=period, interval=interval, start=start_date, end=end_date
    )
    return df


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


def plot_frame(df, filename, entry=None, exit=None):
    plt.figure(figsize=(16, 9), dpi=360)
    plt.plot(df["Close"], label="Close Price")
    plt.plot(df["Final Lowerband"], "g", label="Final Lowerband")
    plt.plot(df["Final Upperband"], "r", label="Final Upperband")
    if entry != None:
        for e in entry:
            plt.plot(
                df.index[e[0]],
                e[1],
                marker="^",
                color="green",
                markersize=12,
                linewidth=0,
                label="Entry",
            )

    if exit != None:
        for e in exit:
            plt.plot(
                df.index[e[0]],
                e[1],
                marker="v",
                color="red",
                markersize=12,
                linewidth=0,
                label="Exit",
            )
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

    if config.dl_start != None:
        start_date = config.dl_start.strftime(capital.CAPITAL_STRING_FORMAT)

    if config.dl_end != None:
        end_date = config.dl_end.strftime(capital.CAPITAL_STRING_FORMAT)

    res = capital.download(
        config.symbol,
        security,
        cst,
        "MINUTE_5",
        start_date=start_date,
        end_date=end_date,
    )

    df, changed = capital.convert_download(res)

    sf = supertrend(changed, config.atr_period, config.atr_multiplier)
    df = changed.join(sf)
    df.index = pd.to_datetime(df.index, format="%Y-%m-%dT%H:%M:%S")

    return df


def trade(config, df):
    pos = capital.get_positions(config.security_token, config.cst_token)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
