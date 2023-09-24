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
        if close.iloc[curr] > final_upperband.iloc[prev]:
            supertrend[curr] = True
        # if current close price crosses below lowerband
        elif close.iloc[curr] < final_lowerband.iloc[prev]:
            supertrend[curr] = False
        # else, the trend continues
        else:
            supertrend[curr] = supertrend[prev]

            # adjustment to the final bands
            if (
                supertrend[curr] is True
                and final_lowerband.iloc[curr] < final_lowerband.iloc[prev]
            ):
                final_lowerband.iloc[curr] = final_lowerband.iloc[prev]
            if (
                supertrend[curr] is False
                and final_upperband.iloc[curr] > final_upperband.iloc[prev]
            ):
                final_upperband.iloc[curr] = final_upperband.iloc[prev]

        # to remove bands according to the trend direction
        if supertrend[curr] is True:
            final_upperband.iloc[curr] = np.nan
        else:
            final_lowerband.iloc[curr] = np.nan

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
        if not in_position and is_uptrend.iloc[i]:
            share = math.floor(equity / close.iloc[i])
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            equity -= share * close.iloc[i]
            entry.append((i, close.iloc[i]))
            in_position = True
            if debug:
                print(
                    f'Buy {share} shares at {round(close.iloc[i],2)} on {df.index[i].strftime("%Y/%m/%d")}'
                )
        # if in position & price is not on uptrend -> sell
        elif in_position and not is_uptrend.iloc[i]:
            equity += share * close.iloc[i] - commission
            # if debug: print(f'EQUITY: {equity} close price: {close[i]}')
            exit.append((i, close.iloc[i]))
            in_position = False
            if debug:
                print(
                    f'Sell at {round(close.iloc[i],2)} on {df.index[i].strftime("%Y/%m/%d")}'
                )
    # if still in position -> sell all share
    if in_position:
        equity += share * close.iloc[i] - commission

    earning = equity - investment
    roi = round(earning / investment * 100, 2)
    if debug:
        print(
            f"Earning from investing ${investment} is ${round(earning,2)} (ROI = {roi} \%)"
        )
    return entry, exit, roi


# BONUS: parameter optimization
def find_optimal_parameter(
    df,
    investment=10000,
    atr_period=[6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    atr_multiplier=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0],
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
