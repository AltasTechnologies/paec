from dataclasses import dataclass

import numpy as np

from .paec_enums import Side, TimeForce


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume_usd: float
    timestamp: float  # timestamp in millis


@dataclass
class OrderBook:
    bids: tuple[np.ndarray, np.ndarray]  # Tuple contain price and size
    asks: tuple[np.ndarray, np.ndarray]  # Tuple contain price and size
    timestamp: float  # timestamp in millis


@dataclass
class Account:
    value_usd: float
    free_value_usd: float


@dataclass
class Order:
    instrument: str
    price: float
    side: Side
    time_force: TimeForce = TimeForce.GTC
