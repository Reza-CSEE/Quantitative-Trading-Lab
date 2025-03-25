import pandas as pd
import yfinance as yf  # برای دانلود داده‌های مالی
import backtrader as bt

# دانلود داده‌های سهام اپل برای ۲ سال گذشته
apple = yf.download("AAPL", start="2022-01-01", end="2024-01-01")

# حل مشکل MultiIndex: تبدیل نام‌های ستون‌ها به ساده
apple.columns = apple.columns.get_level_values(0)  # استخراج نام اصلی ستون‌ها

# نمایش پنج ردیف اول داده‌ها
print(apple.head())

# محاسبه میانگین متحرک 50 روزه
apple['SMA50'] = apple['Close'].rolling(window=50).mean()

# اطمینان از اینکه ستون‌های مورد نیاز در فرمت درست قرار دارند
apple = apple[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

# تبدیل ایندکس دیتافریم به DateTimeIndex
apple.index = pd.to_datetime(apple.index)

class SMAStrategy(bt.Strategy):
    params = (('sma_period', 50),)

    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.sma_period)

    def next(self):
        if self.data.close[0] > self.sma[0]:
            self.buy()
        elif self.data.close[0] < self.sma[0]:
            self.sell()

# اجرای استراتژی روی داده‌های سهام اپل
cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=apple)
cerebro.adddata(data)
cerebro.addstrategy(SMAStrategy)
cerebro.run()
cerebro.plot()
