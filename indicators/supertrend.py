import pandas as pd
import numpy as np
from datetime import datetime
import math
import talib
from numba import njit


@njit
def get_basic_bands(med_price, atr, multiplier):
    matr = multiplier * atr
    upper = med_price + matr
    lower = med_price - matr
    return upper, lower


@njit
def get_final_bands_nb(close, upper, lower):
    trend = np.full(close.shape, np.nan)
    dir_ = np.full(close.shape, 1)
    long = np.full(close.shape, np.nan)
    short = np.full(close.shape, np.nan)

    for i in range(1, close.shape[0]):
        if close[i] > upper[i - 1]:
            dir_[i] = 1
        elif close[i] < lower[i - 1]:
            dir_[i] = -1
        else:
            dir_[i] = dir_[i - 1]
            if dir_[i] > 0 and lower[i] < lower[i - 1]:
                lower[i] = lower[i - 1]
            if dir_[i] < 0 and upper[i] > upper[i - 1]:
                upper[i] = upper[i - 1]

        if dir_[i] > 0:
            trend[i] = long[i] = lower[i]
        else:
            trend[i] = short[i] = upper[i]

    return trend, dir_, long, short


def faster_supertrend_talib(high, low, close, period=7, multiplier=3):
    avg_price = talib.MEDPRICE(high, low)
    atr = talib.ATR(high, low, close, period)
    upper, lower = get_basic_bands(avg_price, atr, multiplier)
    return get_final_bands_nb(close, upper, lower)


def get_indicator(high, low, close, period=7, multiplier=3):
    indicator = np.full(close.shape, np.nan)
    supert, _, superl, supers = faster_supertrend_talib(
        low=low, high=high, close=close, period=period, multiplier=multiplier
    )
    indicator = np.where(
        supert == supers, False, np.where(supert == superl, True, np.nan)
    )
    return indicator, superl, supers


def supertrend(df, atr_period, multiplier):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    # initialize Supertrend column to True
    supert, _, superl, supers = faster_supertrend_talib(
        low=low.to_numpy(),
        high=high.to_numpy(),
        close=close.to_numpy(),
        period=atr_period,
        multiplier=multiplier,
    )
    st = pd.Series(
        np.where(supert == supers, False, np.where(supert == superl, True, np.nan)),
        index=close.index,
    )

    return pd.DataFrame(
        {
            "Supertrend": st,
            "Final Lowerband": superl,
            "Final Upperband": supers,
        },
        index=df.index,
    )


@njit
def backtest(close, indicator, investment, debug=False, commission=5):
    entry = np.full(close.shape, np.nan)
    exit = np.full(close.shape, np.nan)
    # initial condition
    in_position = False
    equity = investment
    share = 0

    for i in range(1, close.shape[0]):
        # if not in position & price is on uptrend -> buy

        if not in_position and indicator[i]:
            share = math.floor(equity / close[i])
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            equity -= share * close[i]
            entry[i] = close[i]
            in_position = True
            if debug:
                print("Buy " + str(share) + " shares at " + str(round(close[i], 2)))
        # if in position & price is not on uptrend -> sell
        elif in_position and not indicator[i]:
            equity += share * close[i] - commission
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            exit[i] = close[i]
            in_position = False
            if debug:
                print(f"Sell at {round(close[i],2)}")
    # if still in position -> sell all share
    if in_position:
        equity += share * close[i] - commission

    earning = equity - investment
    roi = round(earning / investment * 100, 2)
    if debug:
        print(
            "Earning from investing $"
            + str(investment)
            + " is $"
            + str(round(earning, 2))
            + " (ROI = "
            + str(roi)
            + "%)"
        )
    return entry, exit, roi, earning


# BONUS: parameter optimization
def find_optimal_parameter(
    high,
    low,
    close,
    investment=10000,
    atr_period=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    atr_multiplier=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0],
):
    roi_list = np.zeros((len(atr_multiplier) * len(atr_period), 3))

    # for each period and multiplier, perform backtest
    i = 0
    for period, multiplier in [(x, y) for x in atr_period for y in atr_multiplier]:
        roi_list[i][0] = period
        roi_list[i][1] = multiplier
        indicator, _, _ = get_indicator(
            close=close, high=high, low=low, period=period, multiplier=multiplier
        )
        _, _, roi, _ = backtest(close=close, indicator=indicator, investment=investment)
        # roi_list.append((period, multiplier, roi))
        roi_list[i][2] = roi
        i += 1

    # print(pd.DataFrame(roi_list, columns=["ATR_period", "Multiplier", "ROI"]))

    return roi_list
    # return the best parameter set
    # return max(roi_list, key=lambda x: x[2])
