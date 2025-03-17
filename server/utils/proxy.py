import itertools

PROXIES = [
    
]

proxy_cycle = itertools.cycle(PROXIES)

def get_next_proxy():
    proxy = next(proxy_cycle)
    if proxy["type"] == "http":
        return f"http://{proxy["user"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}"
    elif proxy["type"] == "socks5":
        return f"socks5://{proxy["user"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}"
