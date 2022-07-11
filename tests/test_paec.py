import asyncio
import pytest
from paec import Paec
from datetime import timedelta
import numpy as np
import numpy as np

from paec.paec_dataclasses import Order
from paec.paec_enums import Side


@pytest.mark.asyncio
async def test_get_coins():
    coins = await Paec().get_coins()
    assert len(coins) > 0
    assert all(isinstance(coin, str) for coin in coins)


@pytest.mark.asyncio
async def test_ohlcv_data():
    source = Paec().get_ohlcv_data("BTC", timedelta(seconds=0.1))
    acc = 0
    async for candle in source:
        acc += 1
        if acc > 5:
            break

        assert candle.low < candle.high
        assert not np.isnan(
            np.array(
                [candle.open, candle.high, candle.close, candle.low, candle.volume_usd]
            )
        ).all()


@pytest.mark.asyncio
async def test_order_book():
    acc = 0
    source = Paec().get_order_book("BTC")
    async for book in source:
        acc += 1
        if acc > 5:
            break

        bid_prices, bid_sizes = book.bids
        ask_prices, ask_sizes = book.asks
        assert bid_prices[0] < ask_prices[0]
        assert bid_prices[0] > bid_prices[-1]
        assert ask_prices[0] < ask_prices[-1]
        assert bid_sizes[bid_sizes > 0].all()
        assert ask_sizes[ask_sizes > 0].all()


@pytest.mark.asyncio
async def test_balance():
    for _ in range(5):
        account = await Paec().get_balance()
        assert account.value_usd > account.free_value_usd


@pytest.mark.asyncio
async def test_post_order():
    interface = Paec()
    buys = [
        Order(instrument="BTC", price=100 - delta, side=Side.BUY)
        for delta in np.random.lognormal(size=5)
    ]
    sell = [
        Order(instrument="BTC", price=100 + delta, side=Side.BUY)
        for delta in np.random.lognormal(size=5)
    ]

    coros_buy = [interface.post_order(order) for order in buys]
    coros_sell = [interface.post_order(order) for order in sell]
    ids_buy, ids_sell = await asyncio.gather(
        asyncio.gather(*coros_buy), asyncio.gather(*coros_sell)
    )
    assert len(ids_buy) == len(set(ids_buy))
    assert len(ids_sell) == len(set(ids_sell))
    assert not set(ids_buy).intersection(set(ids_sell))


@pytest.mark.asyncio
async def test_post_order():
    interface = Paec()
    instrument = "BTCUSDT"
    interface._orders[instrument] = {42}

    await interface.cancel_order(instrument, 42)

    with pytest.raises(RuntimeError, match="Unknown order"):
        await interface.cancel_order(instrument, 1122)
        raise
