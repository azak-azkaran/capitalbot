import yfinance as yf
import numpy as np
from indicators import supertrend
import matplotlib.pyplot as plt
import os
import time
from main_module import capital
import pandas as pd
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
    high = df["High"].to_numpy()
    low = df["Low"].to_numpy()
    close = df["Close"].to_numpy()
    roi_list = supertrend.find_optimal_parameter(high=high, close=close, low=low)

    optimal_param = max(roi_list, key=lambda x: x[2])
    #optimal_param = supertrend.find_optimal_parameter(df)
    print(
        f"Best parameter {args.symbol} set: ATR Period={optimal_param[0]}, Multiplier={optimal_param[1]}, ROI={optimal_param[2]}%"
    )


def mode_supertrend(df, args, debug=False, plot=True, ):
    if df.empty is True:
        raise ValueError("No values in DataFrame for backtesting")
    if df.index.size <= args.atr_period:
        raise ValueError("Not enough values in DataFrame for backtesting")
    if debug:
        print("Starting Mode Supertrend with: " + str(args))
        print(df)

    st, st_lowerband, st_upperband  = supertrend.get_indicator(df, args.atr_period, args.atr_multiplier)
    entry, exit, roi, earning = supertrend.backtest(df["Close"].to_numpy(), st["Supertrend"].to_numpy(), investment=args.investment, debug=False, commission=args.comission)
    
    df[FINAL_LOWER] = st_lowerband
    df[FINAL_UPPER] = st_upperband
    print(f"Earning from investing ${args.investment} is ${round(earning,2)} (ROI = {roi}%)")

    if plot:
        plot_frame(df, entry=entry, exit=exit, filename=args.filename)


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
        df = download(args.symbol, "5m", start_date=args.dl_start, end_date=args.dl_end)

    if args.mode == "supertrend" or args.mode == "st":
        return mode_supertrend(df, args, debug=args.debug)
    elif args.mode == "console" or args.mode == "it":
        return mode_console(args)
    elif args.mode == "backtest" or args.mode == "backtesting" or args.mode == "bt":
        return mode_backtest(df, args)
    else:
        raise ValueError("No mode specified")


def mode_console(args):
    #while True:
    print("TODO: not yet implemented")
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

    if type( entry ) == pd.DataFrame or type( entry ) == pd.Series or type(entry) == np.ndarray:
        for e in range(entry.shape[0]):
            plt.plot(
                df.index[e],
                entry.iloc[e],
                marker="^",
                color="green",
                markersize=12,
                linewidth=0,
                label="Entry",
            )

    if type( exit ) == pd.DataFrame or type( exit ) == pd.Series or type(exit) == np.ndarray:
        for e in range(exit.shape[0]):
            plt.plot(
                df.index[e],
                exit.iloc[e],
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
