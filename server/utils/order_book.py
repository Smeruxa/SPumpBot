def analyze_order_book(order_book_data):
    try:
        bids, asks = order_book_data["data"]["bids"], order_book_data["data"]["asks"]
        bid_volume, ask_volume = sum(float(b[1]) for b in bids), sum(float(a[1]) for a in asks)
        imbalance = bid_volume / ask_volume if ask_volume else float("inf")

        if imbalance > 2:
            return "Bullish", f"Сильный спрос, Imbalance = {imbalance:.2f}"
        if imbalance < 0.5:
            return "Bearish", f"Сильное давление на продажу, Imbalance = {imbalance:.2f}"
        return "Neutral", f"Imbalance = {imbalance:.2f}"
    except:
        return "Neutral", "Ошибка данных"