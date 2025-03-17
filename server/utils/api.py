import hmac
import time
import aiohttp
import asyncio
from utils.proxy import get_next_proxy
from aiohttp_socks import ProxyConnector
from hashlib import sha256
from config import keys, APIURL, POPULAR_SYMBOLS

key_index = 0

def get_sign(secret, payload):
    return hmac.new(secret.encode(), payload.encode(), sha256).hexdigest()

async def send_request(session, method, path, params):
    global key_index
    params["timestamp"] = str(int(time.time() * 1000))
    query_string = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
    key, secret = keys[key_index]["api_key"], keys[key_index]["secret_key"]
    url = f"{APIURL}{path}?{query_string}&signature={get_sign(secret, query_string)}"
    headers = {"X-BX-APIKEY": key}
    key_index = (key_index + 1) % len(keys)

    proxy_url = get_next_proxy()

    connector = ProxyConnector.from_url(proxy_url)

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.request(method, url, headers=headers, timeout=5) as response:
                await response.text()
                if response.status == 429:
                    return "limit_exceeded", int(response.headers.get("Retry-After", 10))
                return await response.json(), None
    except Exception as e:
        print(f"Request error for {path} via {proxy_url}: {e}")
        return {}, None

async def get_prices():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, symbol) for symbol in POPULAR_SYMBOLS]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        prices = {}
        for result in results:
            if isinstance(result, tuple) and len(result) == 2 and result[1] not in [None, "limit_exceeded"]:
                symbol, price = result
                prices[symbol] = price
        
        return prices

async def fetch_price(session, symbol):
    response, _ = await send_request(session, "GET", "/openApi/swap/v2/quote/premiumIndex", {"symbol": symbol})
    
    if not isinstance(response, dict):
        return symbol, None

    data = response.get("data", {})
    if not isinstance(data, dict):
        return symbol, None

    mark_price = data.get("markPrice")
    if mark_price is None:
        return symbol, None

    try:
        return symbol, float(mark_price)
    except (ValueError, TypeError):
        return symbol, None

async def get_klines(session, symbol):
    path = "/openApi/swap/v3/quote/klines"
    params = {"symbol": symbol, "interval": "1h", "limit": "1000"}

    data, _ = await send_request(session, "GET", path, params)

    if not isinstance(data, dict):
        return symbol, []
    
    return symbol, data.get("data", [])

async def get_order_books(session):
    tasks = [fetch_order_book(session, symbol) for symbol in POPULAR_SYMBOLS]
    return {symbol: data for symbol, data in await asyncio.gather(*tasks)}

async def fetch_order_book(session, symbol):
    path = "/openApi/swap/v2/quote/depth"
    params = {"symbol": symbol, "limit": "5"}
    data, _ = await send_request(session, "GET", path, params)
    return symbol, data
