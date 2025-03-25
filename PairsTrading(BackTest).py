import backtrader as bt
import pandas as pd
import numpy as np
import os
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller



# 📌 **Symbols for Pairs Trading**

TICKER1 = "V"
TICKER2 = "MA"


# 📌 **Load and clean data from CSV**
df = pd.read_csv("/Users/rezaghasemi/Downloads/Programming/Quantitative/pairs_trading_data4.csv", index_col="date", parse_dates=True)

# **🔹 بررسی مقدار `NaN` و حذف سطرهایی که مقدار `NaN` دارند**
df.dropna(inplace=True)

# بررسی داده‌ها قبل از ورود به `Backtrader`
print("Checking data before loading into Backtrader:")
print(df[[TICKER1, TICKER2]].head(10))
print(df.isna().sum())  # بررسی مقدار `NaN`

# 📌 **Define a Custom Pandas Data Feed for Backtrader**
class CustomPandasData(bt.feeds.PandasData):
    params = (
        ("datetime", None),
        ("open", -1),
        ("high", -1),
        ("low", -1),
        ("close", 0),  # Ensuring `close` is mapped properly
        ("volume", -1),
        ("openinterest", -1),
    )


class PairsTradingStrategy(bt.Strategy):
    params = (("lookback", 20), ("entry_z", 1.1), ("exit_z", 0.5))

    def __init__(self):
        self.stock1 = self.datas[0]
        self.stock2 = self.datas[1]
        self.order = None  # **🚀 کلید مدیریت سفارشات**
        
        # **🔹 بررسی مقدار حداقل داده**
        self.addminperiod(self.params.lookback)

        # **🔹 تعریف `spread` به عنوان `line` در `Backtrader`**
        self.l.spread = self.stock1.close - self.stock2.close
        self.l.mean_spread = bt.indicators.SimpleMovingAverage(self.l.spread, period=self.params.lookback)
        self.l.std_spread = bt.indicators.StandardDeviation(self.l.spread, period=self.params.lookback)

        # **🔹 جلوگیری از `NaN` در `Z-Score`**
        self.l.z_score = (self.l.spread - self.l.mean_spread) / (self.l.std_spread + 1e-8)

    def next(self):
        # **🔹 بررسی مقدار `NaN` و حذف آن**
        if np.isnan(self.l.spread[0]) or np.isnan(self.l.mean_spread[0]) or np.isnan(self.l.std_spread[0]) or np.isnan(self.l.z_score[0]):
            print(f"⚠️ Skipping trade due to NaN values: Spread={self.l.spread[0]}, Mean Spread={self.l.mean_spread[0]}, Std Spread={self.l.std_spread[0]}, Z-Score={self.l.z_score[0]}")
            return

        # **🔹 چاپ مقدار `spread`, `mean_spread`, `std_spread` و `Z-Score` برای بررسی وضعیت بازار**
        print(f"Spread: {self.l.spread[0]}, Mean Spread: {self.l.mean_spread[0]}, Std Spread: {self.l.std_spread[0]}, Z-Score: {self.l.z_score[0]}")
        #print(f"self.position: {self.position}")



        # **🔹 ورود به معامله در صورتی که موقعیت باز نداشته باشیم**
        if not self.position:
            if self.z_score[0] < -self.params.entry_z:
                print("📈 Entering Long Position (Stock1 Buy, Stock2 Sell)")
                self.order = self.buy(data=self.stock1, size=10)
                self.order = self.sell(data=self.stock2, size=10)
                return
            if self.z_score[0] > self.params.entry_z:
                print("📉 Entering Short Position (Stock1 Sell, Stock2 Buy)")
                self.order = self.sell(data=self.stock1, size=10)
                self.order = self.buy(data=self.stock2, size=10)
                return
        else: 
            if abs(self.z_score[0]) < self.params.exit_z:
                print("✅ Exiting Position (Closing both trades)")
                self.order = self.close(self.stock1)
                self.order = self.close(self.stock2)
                return  # **🚀 پس از خروج، در این کندل دیگر معامله جدیدی باز نمی‌شود**





# 📌 **Run Backtrader Backtest**
cerebro = bt.Cerebro()

# 📌 **Load Data into Backtrader**
data1 = CustomPandasData(dataname=df[[TICKER1]].dropna())
data2 = CustomPandasData(dataname=df[[TICKER2]].dropna())

cerebro.adddata(data1)
cerebro.adddata(data2)

# 📌 **Add Strategy**
cerebro.addstrategy(PairsTradingStrategy)

# 📌 **Set Initial Capital**
cerebro.broker.set_cash(10000)

# 📌 **Set Trading Commission**
cerebro.broker.setcommission(commission=0.001)

# 📌 **Run Strategy**
print("📊 Initial Portfolio Value: %.2f" % cerebro.broker.getvalue())
cerebro.run()

import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [12, 6]  # تنظیم اندازه نمودار

#cerebro.plot(style='candlestick', volume=False, stdstats=False)

# **🔹 Check and prevent NaN in final portfolio value**
final_value = cerebro.broker.getvalue()
if pd.isna(final_value) or final_value == 10000:
    print("⚠️ Warning: No trades executed. Skipping plot.")
    cerebro.plot(style='candlestick', volume=False, stdstats=False)
else:
    print("📊 Final Portfolio Value: %.2f" % final_value)
    cerebro.plot()
