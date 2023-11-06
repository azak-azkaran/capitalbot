from main_module import config
from main_module import capital
from main_module import main





class Console:
    conf = config.Config()
    get_options = {
        "1": self._supertrend,
        "2": self._backtesting,
    }
    def __init__(self) -> None:
        pass

    def run(self, config):
        conf = config
        self._show_main_menu(config)
        data = input("Please enter the message:\n")
        switch()
        if 'Exit' == data:
            return False
        print(f'Processing Message from input() *****{data}*****')
        df = main.capitalize(self.conf)
        main.mode_supertrend(df, self.conf)
        return True
    
    def _show_main_menu(self):
        print('Menu:')
        print("Current Configuration: Symbol:" + self.conf.symbol)
        print('1: Supertrend')
        print('2: Backtest')
    
    def _supertrend(self):
        print('Supertrend')
