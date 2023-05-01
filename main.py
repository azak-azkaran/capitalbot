import argparse
from supertrend import Supertrend
import yfinance as yf
import matplotlib.pyplot as plt

def yahoo(symbol,period,interval):
    df = yf.download(symbol, period=period,interval=interval)
    return df

def main():
    parser = argparse.ArgumentParser(description="List fish in aquarium.")
    parser.add_argument("symbol", type=str)
    parser.add_argument("period", type=int)
    parser.add_argument("multiplier", type=int)
    parser.add_argument("provider", type=str)
    args = parser.parse_args()
    """
    main
    """

    if(args.provider == "yahoo"):
        df = yahoo(args.symbol, "5d", "1m")
    else:
        df = capital(args.symbol, , )

    supertrend = Supertrend(df, args.period, args.multiplier)
    df = df.join(supertrend)

    plt.plot(df['Close'], label='Close Price')
    plt.plot(df['Final Lowerband'], 'g', label = 'Final Lowerband')
    plt.plot(df['Final Upperband'], 'r', label = 'Final Upperband')
    plt.savefig('foo.png')


if __name__ == "__main__":
    main()