from datetime import datetime, timedelta
import pytz

moscow_tz = pytz.timezone("Europe/Moscow")
current_time = datetime.now(moscow_tz)

one_week = current_time + timedelta(weeks=1)
one_month = current_time + timedelta(days=30)
six_months = current_time + timedelta(days=6 * 30)
one_year = current_time + timedelta(days=365)

print(f"Текущее: {current_time.isoformat()}")
print(f"Неделя: {one_week.isoformat()}")
print(f"Месяц: {one_month.isoformat()}")
print(f"6 месяцев: {six_months.isoformat()}")
print(f"Год: {one_year.isoformat()}")