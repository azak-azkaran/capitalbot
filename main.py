import argparse
from supertrend import supertrend
import yfinance as yf
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="List fish in aquarium.")
    parser.add_argument("symbol", type=str)
    parser.add_argument("period", type=int)
    parser.add_argument("multiplier", type=int)
    args = parser.parse_args()
    """
    main
    """
    df = yf.download(args.symbol, period="5d",interval="2m", )

    supertrend = supertrend(df, args.period, args.multiplier)
    df = df.join(supertrend)

    plt.plot(df['Close'], label='Close Price')
    plt.plot(df['Final Lowerband'], 'g', label = 'Final Lowerband')
    plt.plot(df['Final Upperband'], 'r', label = 'Final Upperband')
    plt.savefig('foo.png')


if __name__ == "__main__":
    main()