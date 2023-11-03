from main_module import config 
from datetime import datetime, timedelta

TEST_CONFIG_PATH = "./tests/test_config.yaml"

def test_parse_args():
    args = config.Config(filename=TEST_CONFIG_PATH)
    assert args != None
    assert args.symbol == "AAPL"
    assert args.atr_period != None
    assert args.atr_period == 3
    assert args.atr_multiplier != None
    assert args.atr_multiplier == 10
    assert args.dl_end != None
    assert args.dl_start != None

def test_parse_period():
    conf = config.Config()
    start, end = conf.parse_period("5d")
    assert datetime.now() - start > timedelta(days=5)
    assert datetime.now() - end < timedelta(days=3)

    try:
        start, end = conf.parse_period("6day")
        assert False
    except ValueError:
        assert True

    start, end = conf.parse_period("1d")
    assert datetime.now() - start > timedelta(days=1)

    start, end = conf.parse_period("1mo")

