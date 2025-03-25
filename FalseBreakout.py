import backtrader as bt
import requests
import pandas as pd
import os

# API Settings
ticker = "AAPL"
start_date = "2023-01-09"
end_date = "2024-12-10"
api_key = "#####################"  # Insert your API Key

# File save path
save_path = f"/Users/rezaghasemi/Downloads/Programming/Quantitative/{ticker}_FalseBreakout_Strategy.csv"

# Check if file already exists
if os.path.exists(save_path):
    print("🔍 File found, loading data...")
    df = pd.read_csv(save_path, index_col="date", parse_dates=True)
else:
    print("📡 Fetching data from API...")
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc&apiKey={api_key}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()["results"]
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["t"], unit="ms")
            df.set_index("date", inplace=True)

            # Rename columns for Backtrader
            df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"}, inplace=True)

            # Save data to CSV
            df.to_csv(save_path)
            print(f"✅ Data saved at: {save_path}")

        except Exception as e:
            print(f"❌ JSON processing error: {e}")
            exit()
    else:
        print(f"❌ API Error: Status code {response.status_code}")
        print("Response text:", response.text)
        exit()


# 📌 **Backtrader Strategy: False Breakout**
class FalseBreakoutStrategy(bt.Strategy):
    params = (("lookback", 40),)  # Lookback period for previous high

    def __init__(self):
        # پیدا کردن بالاترین سقف ۲۰ روز گذشته
        self.prev_high = bt.indicators.Highest(self.data.high, period=self.params.lookback)
        self.bought = False  # متغیر برای پیگیری وضعیت خرید

    def next(self):
        if not self.position:
            # **شرط خرید**: قیمت از سقف قبلی بالاتر رود و در بالای آن بسته شود
            if self.data.high[0] > self.prev_high[-1] and self.data.close[0] > self.prev_high[-1]:
                cash_available = self.broker.get_cash()
                share_size = cash_available * 0.10 / self.data.close[0]  # خرید با ۱۰٪ از سرمایه
                self.buy(size=round(share_size))
                self.bought = True  # علامت‌گذاری که خرید انجام شده

        elif self.bought:
            # **شرط فروش**: شکست نامعتبر → قیمت دوباره به زیر سقف قبلی برگردد
            if self.data.close[0] < self.prev_high[-1]:
                self.sell(size=self.position.size)
                self.bought = False  # بازنشانی وضعیت خرید


# 📊 **Backtrader Engine**
cerebro = bt.Cerebro()

# Load data
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(FalseBreakoutStrategy)

# Set initial cash
cerebro.broker.set_cash(10000)

# Set commission
cerebro.broker.setcommission(commission=0.001)

# Run backtest
print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
cerebro.run()
print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())

# Plot results
cerebro.plot()
