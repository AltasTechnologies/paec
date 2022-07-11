import asyncio
from datetime import datetime, timedelta
import operator
from typing import AsyncIterable, Optional
import numpy as np

from .paec_dataclasses import Candle, OrderBook
from .paec_enums import Side
from .constants import COINS, MAX_DEPTH


class Paec:
    def __init__(self, exchange: str = "PI_EXCHANGE") -> None:
        self._exchange = exchange
        self._prices: dict[str, float] = {
            coin: _compute_hash_coin(coin) for coin in COINS
        }

    async def get_coins(self) -> list[str]:
        """Get all the coins available for trading."""
        await asyncio.sleep(0.1)
        return COINS

    async def get_ohlcv_data(
        self, coin: str, interval: timedelta
    ) -> AsyncIterable[Candle]:
        """Fetch Open, High, Low, Close and volume from the exchange."""
        self._check_coin(coin)
        while True:
            await asyncio.sleep(interval.seconds)
            candle = self._generate_candle(coin)
            self._update_price(coin, candle.close)

            yield candle

    async def get_order_book(
        self, coin: str, depth: int = MAX_DEPTH
    ) -> AsyncIterable[OrderBook]:
        """Return the order book up to a given depth."""
        self._check_coin(coin)
        while True:
            self._update_price(coin)
            await asyncio.sleep(0.1)
            millis = _get_millis()
            bids, asks = self._generate_bids_and_asks(coin, depth)
            yield OrderBook(bids, asks, timestamp=millis)

    def _update_price(self, coin: str, price: Optional[float] = None) -> None:
        if price is None:
            self._prices[coin] += np.random.normal(scale=2)
        else:
            self._prices[coin] = price

    def _generate_candle(self, coin: str) -> Candle:
        millis = _get_millis()
        price = self._prices[coin]
        arr = np.random.normal(loc=0, scale=2, size=3)
        arr.sort()
        low, close, high = arr + price
        volume_usd = 10 * np.random.pareto(1) * price
        candle = Candle(
            open=open,
            high=high,
            low=low,
            close=close,
            volume_usd=volume_usd,
            timestamp=millis,
        )
        return close, candle

    def _generate_bids_and_asks(self, coin: str, depth: int) -> OrderBook:
        depth = max(depth, MAX_DEPTH)
        millis = _get_millis()
        bids = self._generate_price_and_size(coin, depth, size=Side.BUY)
        asks = self._generate_price_and_size(coin, depth, size=Side.SELL)
        return OrderBook(bids=bids, asks=asks, timestamp=millis)

    def generate_price_and_size(
        self, coin: str, depth: int, side: Side
    ) -> tuple(np.ndarray, np.ndarray):
        current_price = self._prices[coin]
        deltas = np.random.lognormal(size=depth)
        fun = operator.add if side == Side.SELL else operator.sub
        prices = fun(current_price, deltas)
        sizes = 10 * np.random.pareto(1, size=depth)
        return prices, sizes

    def _check_coin(self, coin: str) -> None:
        if coin not in COINS:
            raise ValueError(f"Unknown coin: {coin}")


def _compute_hash_coin(coin: str) -> int:
    return 100 * abs(int(str(hash(coin))[:3]))


def _get_millis() -> float:
    return datetime.utcnow().timestamp() * 1000
