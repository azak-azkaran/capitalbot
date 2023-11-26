class position:
    symbol = ""
    size = 0
    leverage = 0
    name = ""
    direction = ""

    def __init__(self, position, market):
        self.symbol = market["epic"]
        self.name = market["instrumentName"]
        self.size = position["size"]
        self.leverage = position["leverage"]
        self.direction = position["direction"]

    def __str__(self) -> str:
        return (
            self.symbol
            + " : "
            + self.name
            + " - "
            + str(self.size)
            + " : "
            + self.direction
        )
