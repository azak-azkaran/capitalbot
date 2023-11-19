import http.client
import numpy as np
import pandas as pd
import yfinance as yf
import backtrader as bt
import vectorbt as vbt
import os
from indicators import supertrend
from datetime import datetime, timedelta
from main_module import main


def test_supertrend():
    df = yf.download("AAPL", period="1d", interval="1h")
    assert df.empty == False
    print(df)
    st = supertrend.supertrend(df, 5, 10)
    assert st.empty == False

    print(st)
    assert st.columns.size == 3
    assert st.index.size >= 1

def test_get_indicator():
    df = yf.download("AAPL", start="2020-01-01", end="2023-11-09", interval='1D')
    atr_period = 7
    atr_multiplier = 3
    investment = 10000
    high = df["High"].to_numpy()
    low = df["Low"].to_numpy()
    close = df["Close"].to_numpy()
    st = supertrend.supertrend(df, atr_period, atr_multiplier)
    entry, exit, roi, earning = supertrend.backtest(close, st["Supertrend"].to_numpy(), investment=investment, debug=False, commission=0)
    print(f"Earning from investing ${investment} is ${round(earning,2)} (ROI = {roi}%)")
    assert len(entry) != 0
    assert len(exit) != 0

    st,_,_ = supertrend.get_indicator(close=close, high=high, low=low)
    entry, exit, roi, earning = supertrend.backtest(close, st, investment=investment, debug=False, commission=0)
    print(f"Earning from investing ${investment} is ${round(earning,2)} (ROI = {roi}%)")
    assert len(entry) != 0
    assert len(exit) != 0



def test_backtest_supertrend():
    foo_filename = "./foo.png"
    if os.path.exists(foo_filename):
        os.remove(foo_filename)

    atr_period = 7
    atr_multiplier = 3

    df = yf.download("AAPL", start="2020-01-01", end="2023-11-09", interval='1D')

    investment = 10000
    st = supertrend.supertrend(df, atr_period, atr_multiplier)
    entry, exit, roi, earning = supertrend.backtest(df["Close"].to_numpy(), st["Supertrend"].to_numpy(), investment=investment, debug=False, commission=0)
    
    print(f"Earning from investing ${investment} is ${round(earning,2)} (ROI = {roi}%)")
    assert len(entry) != 0
    assert len(exit) != 0

    main.plot_frame(df, foo_filename, pd.Series(entry, index=df.index), pd.Series(exit, index=df.index))
    assert os.path.exists("plots/" + foo_filename)


def test_find_optimal_parameter():
    df = yf.download("AAPL", start="2020-01-01", end="2023-11-09", interval='1D')
    high = df["High"].to_numpy()
    low = df["Low"].to_numpy()
    close = df["Close"].to_numpy()
    roi_list = supertrend.find_optimal_parameter(high=high, close=close, low=low)

    print(pd.DataFrame(roi_list, columns=["ATR_period", "Multiplier", "ROI"]).to_markdown())
    optimal_param = max(roi_list, key=lambda x: x[2])
    print(
        f"Best parameter set: ATR Period={optimal_param[0]}, Multiplier={optimal_param[1]}, ROI={optimal_param[2]}"
    )


def test_backtest_supertrend_backtrader():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(supertrend.SuperTrendStrategy)
    data = bt.feeds.PandasData(dataname=yf.download("AAPL", start="2020-01-01", end="2023-11-09", interval='1D'))
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    # Set our desired cash start
    cerebro.broker.setcash(10000.0)
    re = cerebro.run()
    #cerebro.plot()

#def test_backtest_supertrend_vectorbt():
#    df = yf.download("AAPL", start="2020-01-01", end="2023-11-09", interval='1D')
#    high = df["High"]
#    low = df["Low"]
#    close = df["Close"]
#    period = 7
#    multiplier = 3
#    try:
#        periods = np.arange(4, 20)
#        multipliers = np.arange(20, 41) / 10
#        supert, superd, superl, supers = supertrend.faster_supertrend_talib(low=low.to_numpy(), high=high.to_numpy(), close=close.to_numpy(), period=period, multiplier=multiplier)
#
#        superl = pd.DataFrame({ "Final Lowerband": superl }, index=df.index)
#        supers = pd.DataFrame({ "Final upperband": supers }, index=df.index)
#        entries = (superl.isnull()).vbt.signals.fshift()
#        exits = (supers.isnull()).vbt.signals.fshift()
#        pf = vbt.Portfolio.from_signals(
#            close=close, 
#            entries=entries, 
#            exits=exits, 
#            #short_entries=exits,
#            #short_exits=entries,
#            init_cash=10000,
#            #fees=0.001, 
#            #freq='1D',
#        )
#        #date_range = df.index
#        #fig = df["Close"].loc[date_range].rename('Close').vbt.plot()
#        #supers["Final upperband"].loc[date_range].rename('Short').vbt.plot(fig=fig)
#        #superl["Final Lowerband"].loc[date_range].rename('Long').vbt.plot(fig=fig)
#        #fig.show()
#        #pf.sharpe_ratio.vbt.heatmap(
#        #    x_level='st_period', 
#        #    y_level='st_multiplier',
#        #    slider_level='symbol'
#        #)
#        print(pf.stats())
#        assert True
#    except ValueError:
#        assert False



