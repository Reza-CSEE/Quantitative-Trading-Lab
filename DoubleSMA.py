import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# تنظیمات API
ticker = "AAPL"
start_date = "2023-01-09"
end_date = "2024-12-10"
api_key = "BCnibG6TFwiypPXLQW6cqy5cdcLAP0bf"  # API Key را وارد کنید

# مسیر ذخیره فایل
save_path = "/Users/rezaghasemi/Downloads/Programming/Quantitative/AAPL_SMA_Crossover.csv"


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

            # Rename columns for convenience
            df.rename(columns={"c": "close"}, inplace=True)

            # Calculate moving averages
            df["SMA_50"] = df["close"].rolling(window=50).mean()
            df["SMA_200"] = df["close"].rolling(window=200).mean()

            # Trading signals
            df["Signal"] = 0  # Default: No trade
            df.loc[df["SMA_50"] > df["SMA_200"], "Signal"] = 1  # Buy
            df.loc[df["SMA_50"] < df["SMA_200"], "Signal"] = -1  # Sell

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

# Compute Profit and Loss
df["Returns"] = df["close"].pct_change()  # Daily percentage change
df["Strategy Returns"] = df["Signal"].shift(1) * df["Returns"]  # Apply strategy returns
df["Cumulative Strategy Returns"] = (1 + df["Strategy Returns"]).cumprod()  # Cumulative profit/loss

# 📈 Plot Price and Strategy + Cumulative Profit/Loss in one figure
fig, ax = plt.subplots(2, 1, figsize=(14, 12), sharex=True)

# First subplot: Price and Strategy
ax[0].plot(df.index, df["close"], label="Price", color="gray", alpha=0.6)
ax[0].plot(df.index, df["SMA_50"], label="SMA 50", color="blue")
ax[0].plot(df.index, df["SMA_200"], label="SMA 200", color="red")

# Buy signals
buy_signals = df[df["Signal"] == 1]
ax[0].scatter(buy_signals.index, buy_signals["close"], label="Buy", marker="^", color="green", alpha=1)

# Sell signals
sell_signals = df[df["Signal"] == -1]
ax[0].scatter(sell_signals.index, sell_signals["close"], label="Sell", marker="v", color="red", alpha=1)

ax[0].legend()
ax[0].set_title(f"SMA Crossover Strategy for {ticker}")
ax[0].set_ylabel("Closing Price")
ax[0].grid()

# Second subplot: Cumulative Profit/Loss
ax[1].plot(df.index, df["Cumulative Strategy Returns"], label="Cumulative Profit/Loss", color="purple")
ax[1].axhline(y=1, color="black", linestyle="--")  # Reference line at 1 (no profit/loss)

ax[1].legend()
ax[1].set_title("Cumulative Profit/Loss of Strategy")
ax[1].set_xlabel("Date")
ax[1].set_ylabel("Return Multiplier")
ax[1].grid()

plt.tight_layout()
plt.show()