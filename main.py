import backtrader as bt
from main_module import main
import sys
import os
from datetime import datetime
import yfinance as yf
from indicators import movingaverages
from indicators import supertrend
import numpy as np

#if __name__ == "__main__":
#    df = yf.download("AAPL", start="2020-01-01", end="2023-06-09")
#    optimal_param = supertrend.find_optimal_parameter(df.copy())
#
#    print(
#        f"Best parameter set: ATR Period={optimal_param[0]}, Multiplier={optimal_param[1]}, ROI={optimal_param[2]}"
#    )
#
#
#    cerebro = bt.Cerebro()
#    #strats = cerebro.optstrategy(movingaverages.EMAStrategy, period=range(2, 31))
#    strats = cerebro.optstrategy(supertrend.SuperTrendStrategy, period=range(6, 15), multiplier=range(0,7))
#    # cerebro.addstrategy(movingaverages.EMAStrategy, dolog=True)
#
#    # Datas are in a subfolder of the samples. Need to find where the script is
#    # because it could have been called from anywhere
#    data = bt.feeds.PandasData(dataname=df)
#
#    # Add the Data Feed to Cerebro
#    cerebro.adddata(data)
#
#    # Set our desired cash start
#    cerebro.broker.setcash(10000.0)
#    # Add a FixedSize sizer according to the stake
#    #cerebro.addsizer(bt.sizers.FixedSize, stake=10)
#
#    # Set the commission
#    #cerebro.broker.setcommission(commission=0.01)
#
#    # Run over everything
#    # cerebro.run(maxcpus=10)
#
#    #print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
#    re = cerebro.run(maxcpus=1)
#    #print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
#
#    # Plot the result
#    #cerebro.plot()

if __name__ == "__main__":
   sys.exit(main.main(sys.argv[1:]))