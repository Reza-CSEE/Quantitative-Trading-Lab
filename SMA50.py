import pandas as pd
import numpy as np
import yfinance as yf  # برای دانلود داده‌های مالی

# دانلود داده‌های سهام اپل برای ۲ سال گذشته
apple = yf.download("AAPL", start="2022-01-01", end="2024-01-01")
file_path = "/Users/rezaghasemi/Downloads/Programming/Quantitative/AAPL_data.csv"
# نمایش پنج ردیف اول داده‌ها
print(apple.head())
apple.to_csv(file_path)  # ذخیره در فایل CSV
# محاسبه میانگین متحرک 50 روزه
apple['SMA50'] = apple['Close'].rolling(window=50).mean()

# نمایش نمودار قیمت و میانگین متحرک
import matplotlib.pyplot as plt
plt.figure(figsize=(12,6))
plt.plot(apple['Close'], label='AAPL Price')
plt.plot(apple['SMA50'], label='50-day SMA', linestyle='dashed')
plt.legend()
plt.show()
