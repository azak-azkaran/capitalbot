import backtrader as bt
from main_module import main
import sys
import os
from datetime import datetime
import yfinance as yf
from indicators import movingaverages

if __name__ == "__main__":
    cerebro = bt.Cerebro()

    strats = cerebro.optstrategy(movingaverages.EMAStrategy, period=range(10, 31))

    # cerebro.addstrategy(movingaverages.EMAStrategy, dolog=True)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere

    data = bt.feeds.PandasData(dataname=yf.download("TSLA", "2018-01-01", "2019-01-01"))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(1000.0)
    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    # Set the commission
    cerebro.broker.setcommission(commission=0.01)

    # Run over everything
    # cerebro.run(maxcpus=10)

    # print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.run()

    # print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # Plot the result
    # cerebro.plot()

# if __name__ == "__main__":
#    sys.exit(main.main(sys.argv[1:]))
