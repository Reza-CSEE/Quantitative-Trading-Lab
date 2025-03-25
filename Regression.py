import statsmodels.api as sm
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

# دانلود داده‌های سهام اپل برای ۲ سال گذشته
apple = yf.download("AAPL", start="2022-01-01", end="2024-01-01")

# بررسی داده‌ها
if apple is None or apple.empty:
    raise ValueError("Error: Failed to download stock data.")

# محاسبه میانگین متحرک 50 روزه
apple['SMA50'] = apple['Close'].rolling(window=50).mean()

# حذف مقادیر NaN و inf قبل از اجرای رگرسیون
apple.replace([np.inf, -np.inf], np.nan, inplace=True)
apple.dropna(inplace=True)


# متغیر وابسته (قیمت بسته شدن)
Y = apple['Close']

# متغیر مستقل (میانگین متحرک ۵۰ روزه)
X = apple[['SMA50']]
X = sm.add_constant(X)  # اضافه کردن ثابت به مدل

# اجرای رگرسیون خطی
model = sm.OLS(Y, X).fit()

# نمایش نتایج مدل
print(model.summary())

# نمایش نمودار قیمت و میانگین متحرک
plt.figure(figsize=(12,6))
plt.plot(apple['Close'], label='AAPL Price')
plt.plot(apple['SMA50'], label='50-day SMA', linestyle='dashed')
plt.legend()
plt.show()
