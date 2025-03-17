import time
import asyncio
import aiohttp
from utils.api import get_prices, get_klines, get_order_books
from utils.indicators import detect_pump
from config import POPULAR_SYMBOLS, PRICE_HISTORY_SIZE
from telegram.bot import notify_pump

async def monitor_prices():
    price_history = {symbol: [] for symbol in POPULAR_SYMBOLS}

    async with aiohttp.ClientSession() as session:
        while True:
            start_time = time.time()
            prices, order_books = await get_prices(), await get_order_books(session)
            print(prices)
            klines_data = {symbol: klines for symbol, klines in await asyncio.gather(
                *[get_klines(session, symbol) for symbol in POPULAR_SYMBOLS]
            )}

            for symbol, price in prices.items():
                if price == "limit_exceeded":
                    continue
                current_time = time.time()
                price_history[symbol].append((current_time, price))
                price_history[symbol] = price_history[symbol][-PRICE_HISTORY_SIZE:]

                direction, pump_text = detect_pump(symbol, price, price_history[symbol], order_books[symbol], klines_data[symbol])
                if direction:
                    notify_pump(symbol, direction, pump_text)

            await asyncio.sleep(max(0, 5 - (time.time() - start_time)))