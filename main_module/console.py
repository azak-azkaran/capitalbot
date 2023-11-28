from main_module import config
from main_module import capital
from main_module import main


class Console:
    conf = config.Config()

    def __init__(self) -> None:
        pass

    def run(self, conf):
        self.conf = conf
        self._show_main_menu()
        data = input("Please enter the message:\n")

        if data in ("Exit", "exit", "0"):
            return False
        elif data == "1":
            return self._supertrend()
        elif data == "2":
            return self._backtesting()
        elif data == "3":
            return self._change_symbol()
        elif data == "4":
            return self._search_symbol()
        else:
            print("Invalid Message")
        return True

    def _show_main_menu(self):
        print("Menu:")
        print("Current Configuration: Symbol:" + self.conf.symbol)
        print("1: Supertrend")
        print("2: Backtest")
        print("3: Change Symbol")
        print("4: Search Symbol")
        print("0: Exit")

    def _supertrend(self):
        print("Starting Mode Supertrend with: ")
        print("Period: " + str(self.conf.atr_period))
        print("Multiplier: " + str(self.conf.atr_multiplier))
        print("Data Interval: " + str(self.conf.dl_period))
        print("Data Period: " + str(self.conf.dl_interval))
        print("Start: " + self.conf.dl_start.strftime(capital.CAPITAL_STRING_FORMAT))
        print("End: " + self.conf.dl_end.strftime(capital.CAPITAL_STRING_FORMAT))

        df = main.capitalize(self.conf)
        main.mode_supertrend(df, self.conf)

    def _backtesting(self):
        print("Backtesting")
        df = main.capitalize(self.conf)
        main.mode_backtest(df, self.conf)

    def _change_symbol(self):
        data = input("Please enter new Symbol\n")
        print("Changing Symbol: ", data.upper())
        self.conf.symbol = data.upper()

    def _search_symbol(self):
        print("Search Symbol")
