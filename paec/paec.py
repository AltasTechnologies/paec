import asyncio
import operator
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, AsyncIterable, DefaultDict, Optional

import numpy as np

from .constants import COINS, MAX_DEPTH
from .paec_dataclasses import Account, Candle, Order, OrderBook
from .paec_enums import Side


class Paec:
    def __init__(self, exchange: str = "PI_EXCHANGE") -> None:
        self._exchange = exchange
        self._prices: dict[str, float] = {
            coin: np.random.randint(10, 1000) for coin in COINS
        }
        self._orders: DefaultDict[str, set[int]] = defaultdict(set)

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
            yield self._generate_order_book(coin, depth)

    async def get_balance(self) -> Account:
        await asyncio.sleep(0.1)
        value_usd = np.random.randint(20000, 1000000)
        return Account(value_usd=value_usd, free_value_usd=value_usd - 10000)

    async def post_order(self, order: Order) -> int:
        await asyncio.sleep(0.1)
        id = np.random.randint(100, 100000000)
        self._orders[order.instrument].add(id)
        return id

    async def cancel_order(self, instrument: str, id: int) -> None:
        pred = instrument not in self._orders
        if pred or id not in self._orders[instrument]:
            raise RuntimeError(f"Unknown order {id} for instrument: {instrument}")
        await asyncio.sleep(0.1)
        self._orders[instrument].remove(id)

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
            open=price,
            high=high,
            low=low,
            close=close,
            volume_usd=volume_usd,
            timestamp=millis,
        )
        return candle

    def _generate_order_book(self, coin: str, depth: int) -> OrderBook:
        depth = max(depth, MAX_DEPTH)
        millis = _get_millis()
        bids = self._generate_price_and_size(coin, depth, side=Side.BUY)
        asks = self._generate_price_and_size(coin, depth, side=Side.SELL)
        return OrderBook(bids=bids, asks=asks, timestamp=millis)

    def _generate_price_and_size(
        self, coin: str, depth: int, side: Side
    ) -> tuple[np.ndarray, np.ndarray]:
        current_price = self._prices[coin]
        deltas = np.random.lognormal(size=depth)
        deltas.sort()
        fun = operator.add if side == Side.SELL else operator.sub
        prices = fun(current_price, deltas)
        sizes = 10 * np.random.pareto(1, size=depth)
        sizes.sort()
        return prices, sizes

    def _check_coin(self, coin: str) -> None:
        if coin not in COINS:
            raise ValueError(f"Unknown coin: {coin}")


def _get_millis() -> float:
    return datetime.utcnow().timestamp() * 1000
