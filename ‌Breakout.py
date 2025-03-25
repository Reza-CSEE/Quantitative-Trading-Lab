import backtrader as bt
import requests
import pandas as pd
import datetime as dt
import os

# API Settings
ticker = "AAPL"
start_date = "2023-01-09"
end_date = "2024-12-10"
api_key = "#####################"  # Insert your API Key

# File save path
save_path = f"/Users/rezaghasemi/Downloads/Programming/Quantitative/{ticker}_Breakout.csv"

# Check if file already exists
if os.path.exists(save_path):
    print("🔍 File found, loading data...")
    df = pd.read_csv(save_path, index_col="date", parse_dates=True)
else:
    print("📡 Fetching data from API...")
    # Fetch data from Polygon.io
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc&apiKey={api_key}"
    response = requests.get(url)

    # Check API response status
    if response.status_code == 200:
        try:
            data = response.json()["results"]  # Extract data
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["t"], unit="ms")  # Convert timestamp to date
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


# 📌 **Backtrader Strategy: Breakout Strategy**
class BreakoutStrategy(bt.Strategy):
    params = (("lookback", 20),)  # 20-day breakout period

    def __init__(self):
        self.highest_high = bt.ind.Highest(self.data.high, period=self.params.lookback)  # 20-day highest high
        self.lowest_low = bt.ind.Lowest(self.data.low, period=self.params.lookback)  # 20-day lowest low

    def next(self):
        # Check if we have an open position
        if not self.position:
            if self.data.close[0] > self.highest_high[-1]:  # Breakout above resistance
                self.buy()
        else:
            if self.data.close[0] < self.lowest_low[-1]:  # Drop below support
                self.sell()


# 📊 **Backtrader Engine**
cerebro = bt.Cerebro()

# Load data
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(BreakoutStrategy)

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
