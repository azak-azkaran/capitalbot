import pandas as pd
import numpy as np
from datetime import datetime
import math


def supertrend(df, atr_period, multiplier):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    # calculate ATR
    price_diffs = [high - low, high - close.shift(), close.shift() - low]
    true_range = pd.concat(price_diffs, axis=1)
    true_range = true_range.abs().max(axis=1)
    # default ATR calculation in supertrend indicator
    atr = true_range.ewm(alpha=1 / atr_period, min_periods=atr_period).mean()
    # df['atr'] = df['tr'].rolling(atr_period).mean()

    # HL2 is simply the average of high and low prices
    hl2 = (high + low) / 2
    # upperband and lowerband calculation
    # notice that final bands are set to be equal to the respective bands
    final_upperband = upperband = hl2 + (multiplier * atr)
    final_lowerband = lowerband = hl2 - (multiplier * atr)

    # initialize Supertrend column to True
    supertrend = [True] * len(df)

    for i in range(1, len(df.index)):
        curr, prev = i, i - 1

        # if current close price crosses above upperband
        if close[curr] > final_upperband[prev]:
            supertrend[curr] = True
        # if current close price crosses below lowerband
        elif close[curr] < final_lowerband[prev]:
            supertrend[curr] = False
        # else, the trend continues
        else:
            supertrend[curr] = supertrend[prev]

            # adjustment to the final bands
            if (
                supertrend[curr] == True
                and final_lowerband[curr] < final_lowerband[prev]
            ):
                final_lowerband[curr] = final_lowerband[prev]
            if (
                supertrend[curr] == False
                and final_upperband[curr] > final_upperband[prev]
            ):
                final_upperband[curr] = final_upperband[prev]

        # to remove bands according to the trend direction
        if supertrend[curr] == True:
            final_upperband[curr] = np.nan
        else:
            final_lowerband[curr] = np.nan

    return pd.DataFrame(
        {
            "Supertrend": supertrend,
            "Final Lowerband": final_lowerband,
            "Final Upperband": final_upperband,
        },
        index=df.index,
    )


def backtest_supertrend(df, investment, debug=False, commission=5):
    is_uptrend = df["Supertrend"]
    close = df["Close"]

    # initial condition
    in_position = False
    equity = investment
    share = 0
    entry = []
    exit = []

    for i in range(2, len(df)):
        # if not in position & price is on uptrend -> buy
        if not in_position and is_uptrend[i]:
            share = math.floor(equity / close[i])
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            equity -= share * close[i]
            entry.append((i, close[i]))
            in_position = True
            if debug:
                print(
                    f'Buy {share} shares at {round(close[i],2)} on {df.index[i].strftime("%Y/%m/%d")}'
                )
        # if in position & price is not on uptrend -> sell
        elif in_position and not is_uptrend[i]:
            equity += share * close[i] - commission
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            exit.append((i, close[i]))
            in_position = False
            if debug:
                print(
                    f'Sell at {round(close[i],2)} on {df.index[i].strftime("%Y/%m/%d")}'
                )
    # if still in position -> sell all share
    if in_position:
        equity += share * close[i] - commission

    earning = equity - investment
    roi = round(earning / investment * 100, 2)
    if debug:
        print(
            f"Earning from investing ${investment} is ${round(earning,2)} (ROI = {roi}%)"
        )
    return entry, exit, roi


# BONUS: parameter optimization
def find_optimal_parameter(
    df,
    investment=10000,
    atr_period=[7, 8, 9, 10],
    atr_multiplier=[1.0, 1.5, 2.0, 2.5, 3.0],
):
    roi_list = []

    # for each period and multiplier, perform backtest
    for period, multiplier in [(x, y) for x in atr_period for y in atr_multiplier]:
        new_df = df
        st = supertrend(df, period, multiplier)
        new_df = df.join(st)
        new_df = new_df[period:]
        _, _, roi = backtest_supertrend(new_df, investment)
        roi_list.append((period, multiplier, roi))

    print(pd.DataFrame(roi_list, columns=["ATR_period", "Multiplier", "ROI"]))

    # return the best parameter set
    return max(roi_list, key=lambda x: x[2])
