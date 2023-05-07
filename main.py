import argparse
from supertrend import supertrend
import yfinance as yf
import matplotlib.pyplot as plt
import yaml
import sys
import os

class Config:
    symbol = ""
    atr_period = 0
    atr_multiplier = 0
    dl_period = ""
    dl_interval = ""
    dl_start = None
    dl_end = None


def parse_args(filename):
    with open(filename, 'r') as file:
        conf = yaml.safe_load(file)
        
        args = Config()
        args.symbol = conf.get('symbol')
        if conf.get("atr") == None:
            raise ValueError("atr must be specified")
            
        args.atr_period = conf.get('atr').get("period")
        if args.atr_period == None:
            raise ValueError("atr.period must be specified")
        args.atr_multiplier = conf.get('atr').get('multiplier')
        if args.atr_multiplier == None:
            raise ValueError("atr.multiplier must be specified")
    return args

def download(symbol, interval , period="max", save_to_file=False, start_date=None, end_date=None):
    df = yf.download(tickers=symbol, period=period, interval=interval, start=start_date, end=end_date)
    if save_to_file:
        path = os.path.join("./"+ symbol+".json")
        df.to_json(path_or_buf=path)
    return df


def main(args):
    """
    main
    """
    args = parse_args()
    df = download(args.symbol, "5d", "1m")
    supertrend_frame = supertrend(df, args.period, args.multiplier)
    df = df.join(supertrend_frame)

    plt.plot(df['Close'], label='Close Price')
    plt.plot(df['Final Lowerband'], 'g', label = 'Final Lowerband')
    plt.plot(df['Final Upperband'], 'r', label = 'Final Upperband')
    plt.savefig('foo.png')


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))