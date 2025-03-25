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
save_path = f"/Users/rezaghasemi/Downloads/Programming/Quantitative/{ticker}_RSI_EMA_Strategy.csv"

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


# 📌 **Backtrader Strategy: RSI + EMA Crossover**
class RSI_EMA_Strategy(bt.Strategy):
    params = (("rsi_period", 14), ("rsi_lower", 30), ("rsi_upper", 70), ("ema_short", 20), ("ema_long", 50))  # RSI & EMA Parameters

    def __init__(self):
        # Indicators
        self.rsi = bt.indicators.RSI(period=self.params.rsi_period)
        self.ema_short = bt.indicators.ExponentialMovingAverage(period=self.params.ema_short)
        self.ema_long = bt.indicators.ExponentialMovingAverage(period=self.params.ema_long)

    def next(self):
        if not self.position:
            # Buy Condition: RSI < 30 and EMA 20 crosses above EMA 50
            if self.rsi[0] < self.params.rsi_lower and self.ema_short[0] > self.ema_long[0]:
                cash_available = self.broker.get_cash()
                share_size = cash_available * 0.10 / self.data.close[0]  # Buy with 10% of capital
                self.buy(size=round(share_size))
        else:
            # Sell Condition: RSI > 70 and EMA 20 crosses below EMA 50
            if self.rsi[0] > self.params.rsi_upper and self.ema_short[0] < self.ema_long[0]:
                self.sell(size=self.position.size)


# 📊 **Backtrader Engine**
cerebro = bt.Cerebro()

# Load data
data = bt.feeds.PandasData(dataname=df)
cerebro.adddata(data)

# Add strategy
cerebro.addstrategy(RSI_EMA_Strategy)

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
