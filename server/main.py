import asyncio
from monitor import monitor_prices

if __name__ == "__main__":
    asyncio.run(monitor_prices())