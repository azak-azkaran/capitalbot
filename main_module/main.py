import argparse
import yfinance as yf
from indicators import supertrend
import matplotlib.pyplot as plt
import os
import time
from main_module import capital
import pandas as pd
import backtrader as bt
from backtrader import plot as btplot
from main_module import config


FINAL_UPPER = "Final Upperband"
FINAL_LOWER = "Final Lowerband"


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


def mode_backtest(df, args):
    optimal_param = supertrend.find_optimal_parameter(df)
    print(
        f"Best parameter {args.symbol} set: ATR Period={optimal_param[0]}, Multiplier={optimal_param[1]}, ROI={optimal_param[2]}%"
    )


def mode_supertrend(df, args, debug=False):
    if df.empty is True:
        raise ValueError("No values in DataFrame for backtesting")
    if df.index.size <= args.atr_period:
        raise ValueError("Not enough values in DataFrame for backtesting")
    if debug:
        print("Starting Mode Supertrend with: " + str(args))
        print(df)

    cerebro = bt.Cerebro()
    strats = cerebro.addstrategy(
        supertrend.SuperTrendStrategy,
        period=args.atr_period,
        multiplier=args.atr_multiplier,
    )
    # supertrend_frame = supertrend.supertrend(df, args.atr_period, args.atr_multiplier)
    data = bt.feeds.PandasData(dataname=df)
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    re = cerebro.run()
    pl = cerebro.plot(iplot=False, use="AGG")
    save_backtrader_plot(pl, args, debug=args.debug)


def _save_backtrader_fig(fig, args, index=0, debug=False):
    if args.filename is None:
        filename = (
            args.symbol
            + "_-_"
            + args.dl_start.strftime(capital.CAPITAL_STRING_FORMAT)
            + "_-_"
            + args.dl_end.strftime(capital.CAPITAL_STRING_FORMAT)
            + "_-_"
            + str(index)
            + ".png"
        )
    else:
        filename = args.filename
    filename = "plots/" + filename
    if debug:
        print("saving to file:" + filename) 
    fig.savefig(filename)


def save_backtrader_plot(pl, args, debug=False):
    if type(pl) is list:
        index = 1
        for entry in pl:
            if type(entry) is list:
                for i in entry:
                    _save_backtrader_fig(i, args, index, debug)
                    index += 1
            else:
                _save_backtrader_fig(i, args, index, debug)
    else:
        _save_backtrader_fig(
            i,
            args,
            index,
            debug,
        )


def main(argv):
    """
    main
    """
    args = config.Config(argv[0])
    if args.capital_api_key != "":
        print("Loading from capital")
        print(args)
        df = capitalize(args)

    else:
        print("Loading from yahoo")
        # TODO: change this to be dynamic
        df = download(args.symbol, "5m", start_date=args.start_date, end_date=args.end_date)

    if args.mode == "supertrend" or args.mode == "st":
        return mode_supertrend(df, args, debug=args.debug)
    elif args.mode == "constant_supertrend" or args.mode == "c_st":
        return mode_constant_supertrend(args)
    elif args.mode == "backtest" or args.mode == "backtesting" or args.mode == "bt":
        return mode_backtest(df, args)
    else:
        raise ValueError("No mode specified")


def mode_constant_supertrend(args):
    while True:
        df = capitalize(args)
        mode_supertrend(df, args)
        time.sleep(60)
    print("dying")


def plot_frame(df, filename, entry=None, exit=None):
    if not os.path.exists("plots"):
        os.makedirs("plots")

    filename = "plots/" + filename
    plt.figure(figsize=(16, 9), dpi=360)
    plt.plot(df["Close"], label="Close Price")

    if FINAL_LOWER in df.columns:
        plt.plot(df[FINAL_LOWER], "g", label=FINAL_LOWER)

    if FINAL_UPPER in df.columns:
        plt.plot(df[FINAL_UPPER], "r", label=FINAL_UPPER)

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

    _, changed = capital.convert_download(res)
    changed.index = pd.to_datetime(changed.index, format=capital.CAPITAL_STRING_FORMAT)
    return changed


def trade(config, df):
    pos = capital.get_positions(config.security_token, config.cst_token)
