import backtrader as bt
import requests
import pandas as pd
import numpy as np
import os

# API Settings
ticker = "AAPL"
start_date = "2023-01-09"
end_date = "2024-12-10"
api_key = "#####################"  # Insert your API Key

# File save path
save_path = f"/Users/rezaghasemi/Downloads/Programming/Quantitative/{ticker}_MeanReversion_Strategy.csv"

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


# 📌 **Backtrader Strategy: Mean Reversion using Z-Score**
class MeanReversionStrategy(bt.Strategy):
    params = (("lookback", 20), ("z_score_buy", -2), ("z_score_sell", 2))  # Parameters for mean reversion

    def __init__(self):
        # Compute Moving Average and Standard Deviation
        self.sma = bt.indicators.SimpleMovingAverage(period=self.params.lookback)
        self.std_dev = bt.indicators.StandardDeviation(period=self.params.lookback)

        # Compute Z-Score
        self.z_score = (self.data.close - self.sma) / self.std_dev

    def next(self):
        if not self.position:
            # Buy when Z-Score < -2 (Price is far below mean)
            if self.z_score[0] < self.params.z_score_buy:
                cash_available = self.broker.get_cash()
                share_size = cash_available * 0.10 / self.data.close[0]  # Buy with 10% of capital
                self.buy(size=round(share_size))
        else:
            # Sell when Z-Score > 2 (Price is far above mean)
            if self.z_score[0] > self.params.z_score_sell:
                self.sell(size=self.position.size)


# 📊 **Backtrader Engine**
cerebro = bt.Cerebro()

# Load data
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(MeanReversionStrategy)

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
