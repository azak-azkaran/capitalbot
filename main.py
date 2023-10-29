import backtrader as bt
from main_module import main
import sys
import os
from datetime import datetime
import yfinance as yf
from indicators import movingaverages

if __name__ == "__main__":
    cerebro = bt.Cerebro()

    cerebro.addstrategy(movingaverages.EMAStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere

    data = bt.feeds.PandasData(dataname=yf.download("TSLA", "2018-01-01", "2019-01-01"))

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())

    cerebro.run()

    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot()

# if __name__ == "__main__":
#    sys.exit(main.main(sys.argv[1:]))
