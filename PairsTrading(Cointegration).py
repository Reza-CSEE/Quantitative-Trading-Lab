import requests
import pandas as pd
import numpy as np
import statsmodels.api as sm
import os
from statsmodels.tsa.stattools import adfuller

# 📌 **Retrieve historical stock data from Polygon.io**
API_KEY = "BCnibG6TFwiypPXLQW6cqy5cdcLAP0bf"  # 🔹 Insert your API Key
#TICKER1 = "MSFT"
#TICKER1 = "BRK.A"
TICKER1 = "V"

#TICKER2 = "AAPL"
#TICKER2 = "BRK.B"
TICKER2 = "MA"

START_DATE = "2023-01-01"
END_DATE = "2024-01-01"

# 📌 **Function to fetch stock data from Polygon.io**
def get_stock_data(ticker):
    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{START_DATE}/{END_DATE}?adjusted=true&sort=asc&apiKey={API_KEY}"
    
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()["results"]
            df = pd.DataFrame(data)
            df["date"] = pd.to_datetime(df["t"], unit="ms")
            df.set_index("date", inplace=True)
            df.rename(columns={"c": "close"}, inplace=True)  # Use closing price
            return df[["close"]]
        except Exception as e:
            print(f"❌ Error processing {ticker} data: {e}")
            return None
    else:
        print(f"❌ API request failed for {ticker}. Status code: {response.status_code}")
        return None

# Retrieve stock data
df1 = get_stock_data(TICKER1)
df2 = get_stock_data(TICKER2)

# Merge data into a single DataFrame
df = pd.concat([df1, df2], axis=1)
df.columns = [TICKER1, TICKER2]
df.dropna(inplace=True)

# Save data for Backtrader
df.to_csv("/Users/rezaghasemi/Downloads/Programming/Quantitative/pairs_trading_data4.csv")

# 📌 **Check correlation between the two stocks**
correlation = df.corr().iloc[0, 1]
print(f"✅ Correlation between {TICKER1} and {TICKER2}: {correlation:.2f}")

# 📌 **Perform Cointegration Test**
def cointegration_test(series1, series2):
    model = sm.OLS(series1, sm.add_constant(series2)).fit()
    residuals = model.resid
    adf_result = adfuller(residuals)
    return adf_result[1]  # p-value from ADF test

p_value = cointegration_test(df[TICKER1], df[TICKER2])
print(f"✅ Cointegration test p-value: {p_value:.4f}")

if p_value < 0.05:
    print("✅ The stock pair is cointegrated, suitable for Pairs Trading!")
else:
    print("❌ The stock pair is NOT cointegrated, Pairs Trading may not be reliable.")
