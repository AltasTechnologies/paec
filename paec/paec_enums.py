from enum import Enum


class TimeForce(Enum):
    GTC = 0  # Good till cancel
    IOC = 1  # Immediate-Or-Cancel
    FOK = 2  # Fill or Cancel


class Side(Enum):
    BUY = 0
    SELL = 1
