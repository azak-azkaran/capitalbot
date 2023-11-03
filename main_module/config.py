import yaml
from datetime import datetime, timedelta

class Config:
    symbol = ""
    atr_period = 0
    atr_multiplier = 0
    dl_period = ""
    dl_interval = ""
    dl_start = None
    dl_end = None
    capital_api_key = ""
    capital_password = ""
    capital_identifier = ""
    capital_security_token = ""
    capital_cst_token = ""
    filename = None
    mode = None
    demo = True
    start_date = None
    end_date = None
    debug = False

    def __init__(self, filename=None):
        self.start_date = datetime.now()
        self.end_date = datetime.now()
        if filename is not None:
            self.parse_args(filename)

    def __str__(self) -> str:
        if self.capital_api_key != "":
            return "API KEY: " + self.capital_api_key + " " + self.capital_password
        else:
            return "None Capital Mode"

    def parse_period(self, period):
        # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y
        days = 0
        months = 0
        years = 0
        if period.endswith("d"):
            days = int(period.split("d")[0])
        elif period.endswith("mo"):
            months = int(period.split("mo")[0])
        elif period.endswith("y"):
            years = int(period.split("y")[0])
        else:
            raise ValueError(
                "Period needs to end with: d for days, mo for months and y for years"
            )

        date = datetime.now()
        self.start_date = date - timedelta(days=days)

        if months > 0:
            self.start_date = self.start_date.month - months

        if years > 0:
            self.start_date = self.start_date.year - years

        self.end_date = date - timedelta(hours=2)
        return self.start_date, self.end_date


    def parse_args(self, filename):
        with open(filename, "r") as file:
            conf = yaml.safe_load(file)

            self.symbol = conf.get("symbol")
            if conf.get("atr") == None:
                raise ValueError("atr must be specified")

            self.atr_period = conf.get("atr").get("period")
            if self.atr_period == None:
                raise ValueError("atr.period must be specified")
            self.atr_multiplier = conf.get("atr").get("multiplier")
            if self.atr_multiplier == None:
                raise ValueError("atr.multiplier must be specified")

            if conf.get("capital") != None:
                self.capital_api_key = conf.get("capital").get("api_key")
                self.capital_password = conf.get("capital").get("password")
                self.capital_identifier = conf.get("capital").get("identifier")

            if conf.get("period") != None:
                start, end = self.parse_period(conf.get("period"))
                self.dl_start = start
                self.dl_end = end

            if conf.get("start") != None:
                self.dl_start = conf.get("start")

            if conf.get("end") != None:
                self.dl_end = conf.get("end")

            if conf.get("filename") != None:
                self.filename = conf.get("filename")

            if conf.get("mode") != None:
                self.mode = conf.get("mode")
            
            if conf.get("debug") != None:
                self.debug = conf.get("debug")