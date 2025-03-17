import numpy as np
from utils.order_book import analyze_order_book

def detect_pump(symbol, current_price, price_window, order_book_data, klines):
    prices = [p for _, p in price_window]
    if len(prices) < 5 or not klines:
        return None, ""

    indicators = {
        "sma_50": calculate_sma(prices, 50),
        "sma_200": calculate_sma(prices, 200),
        "ema_20": calculate_ema(prices, 20),
        "rsi": calculate_rsi(prices) or 50,
        "volatility": calculate_volatility(klines) or 0,
        "adx": calculate_adx(klines) or 0,
        "macd": calculate_macd(prices),
        "stochastic": calculate_stochastic(klines),
        "upper_band": None,
        "lower_band": None,
    }

    if len(prices) >= 20:
        indicators["upper_band"], indicators["lower_band"] = calculate_bollinger_bands(prices)

    order_imbalance, imbalance_text = analyze_order_book(order_book_data)

    def format_value(value):
        return f"{value:.8f}" if isinstance(value, (int, float)) else "N/A"

    buy_conditions = [
        order_imbalance == "Bullish",
        indicators["rsi"] is not None and indicators["rsi"] > 70,
        indicators["adx"] is not None and indicators["adx"] > 25,
        indicators["macd"]["macd"] is not None and indicators["macd"]["signal"] is not None and indicators["macd"]["macd"] > indicators["macd"]["signal"],
        indicators["stochastic"]["k"] is not None and indicators["stochastic"]["d"] is not None and indicators["stochastic"]["k"] > indicators["stochastic"]["d"],
        current_price > (indicators["sma_50"] or float("-inf")) * 1.01,
        current_price > (indicators["upper_band"] or float("-inf")),
    ]

    if all(buy_conditions):
        return "Лонг", f"Цена: {format_value(current_price)}, {imbalance_text}, RSI: {format_value(indicators["rsi"])}, ADX: {format_value(indicators["adx"])}, MACD: {format_value(indicators["macd"]["macd"])}, Stochastic K: {format_value(indicators["stochastic"]["k"])}"

    sell_conditions = [
        order_imbalance == "Bearish",
        indicators["rsi"] is not None and indicators["rsi"] < 30,
        indicators["adx"] is not None and indicators["adx"] > 25,
        indicators["macd"]["macd"] is not None and indicators["macd"]["signal"] is not None and indicators["macd"]["macd"] < indicators["macd"]["signal"],
        indicators["stochastic"]["k"] is not None and indicators["stochastic"]["d"] is not None and indicators["stochastic"]["k"] < indicators["stochastic"]["d"],
        current_price < (indicators["sma_50"] or float("inf")) * 0.99,
        current_price < (indicators["lower_band"] or float("inf")),
    ]
    
    if all(sell_conditions):
        return "Шорт", f"Цена: {format_value(current_price)}, {imbalance_text}, RSI: {format_value(indicators["rsi"])}, ADX: {format_value(indicators["adx"])}, MACD: {format_value(indicators["macd"]["macd"])}, Stochastic K: {format_value(indicators["stochastic"]["k"])}"

    return None, ""

def calculate_sma(prices, window):
    if len(prices) < window:
        return None
    return np.mean(prices[-window:])

def calculate_ema(prices, window):
    if len(prices) < window:
        return None
    ema = np.mean(prices[:window])
    alpha = 2 / (window + 1)
    for price in prices[window:]:
        ema = (price - ema) * alpha + ema
    return ema

def calculate_rsi(prices, window=14):
    if len(prices) < window + 1:
        return None
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[:window])
    avg_loss = np.mean(losses[:window])

    for i in range(window, len(gains)):
        avg_gain = (avg_gain * (window - 1) + gains[i]) / window
        avg_loss = (avg_loss * (window - 1) + losses[i]) / window

    if avg_loss == 0:
        return 100

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_volatility(klines):
    if len(klines) < 20:
        return None
    close_prices = [float(k["close"]) for k in klines]
    return np.std(close_prices)

def calculate_bollinger_bands(prices, window=20, std_factor=2):
    if len(prices) < window:
        return None, None
    sma = calculate_sma(prices, window)
    std_dev = np.std(prices[-window:])
    return sma + (std_factor * std_dev), sma - (std_factor * std_dev)

def calculate_adx(klines, window=14):
    if len(klines) < window + 1:
        return None
    high = np.array([float(k["high"]) for k in klines])
    low = np.array([float(k["low"]) for k in klines])
    close = np.array([float(k["close"]) for k in klines])

    tr = np.maximum(high[1:] - low[1:], np.maximum(abs(high[1:] - close[:-1]), abs(low[1:] - close[:-1])))
    dm_plus = np.where((high[1:] - high[:-1]) > (low[:-1] - low[1:]), np.maximum(high[1:] - high[:-1], 0), 0)
    dm_minus = np.where((low[:-1] - low[1:]) > (high[1:] - high[:-1]), np.maximum(low[:-1] - low[1:], 0), 0)

    atr = np.convolve(tr, np.ones(window)/window, mode="valid")
    di_plus = 100 * (np.convolve(dm_plus, np.ones(window)/window, mode="valid") / atr)
    di_minus = 100 * (np.convolve(dm_minus, np.ones(window)/window, mode="valid") / atr)

    dx = np.abs(di_plus - di_minus) / (di_plus + di_minus + 1e-9) * 100
    adx = np.convolve(dx, np.ones(window)/window, mode="valid")

    return adx[-1] if len(adx) > 0 else None

def calculate_macd(prices, short_window=12, long_window=26, signal_window=9):
    if len(prices) < long_window + signal_window:
        return {"macd": None, "signal": None}
    short_ema = calculate_ema(prices, short_window)
    long_ema = calculate_ema(prices, long_window)
    macd = short_ema - long_ema
    signal = calculate_ema(prices[-long_window:], signal_window)
    return {"macd": macd, "signal": signal}

def calculate_stochastic(klines, window=14, smooth_k=3):
    if len(klines) < window + smooth_k:
        return {"k": None, "d": None}
    high = np.array([float(k["high"]) for k in klines])
    low = np.array([float(k["low"]) for k in klines])
    close = np.array([float(k["close"]) for k in klines])

    k_values = []
    for i in range(window, len(close)):
        highest_high = np.max(high[i - window:i])
        lowest_low = np.min(low[i - window:i])
        k = 100 * ((close[i] - lowest_low) / (highest_high - lowest_low))
        k_values.append(k)

    k_smoothed = np.convolve(k_values, np.ones(smooth_k)/smooth_k, mode="valid")
    d_smoothed = np.convolve(k_smoothed, np.ones(smooth_k)/smooth_k, mode="valid")

    return {"k": k_smoothed[-1], "d": d_smoothed[-1]}