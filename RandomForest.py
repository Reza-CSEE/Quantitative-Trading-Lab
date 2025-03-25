import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# 📌 **۱. دریافت داده‌های تاریخی از Polygon.io**
API_KEY = "BCnibG6TFwiypPXLQW6cqy5cdcLAP0bf"
TICKER = "AAPL"
START_DATE = "2023-01-01"
END_DATE = "2024-01-01"

url = f"https://api.polygon.io/v2/aggs/ticker/{TICKER}/range/1/day/{START_DATE}/{END_DATE}?adjusted=true&sort=asc&apiKey={API_KEY}"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data["results"])
    df["date"] = pd.to_datetime(df["t"], unit="ms")
    df.set_index("date", inplace=True)
    df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"}, inplace=True)
else:
    print(f"⚠️ Error fetching data: {response.status_code}, {response.text}")
    exit()

# 📌 **۲. ساخت ویژگی‌های تکنیکال**
df["SMA_20"] = df["Close"].rolling(20).mean()
df["SMA_50"] = df["Close"].rolling(50).mean()
df["RSI"] = 100 - (100 / (1 + df["Close"].pct_change().rolling(14).mean()))
df["Volatility"] = df["Close"].rolling(20).std()

# 📌 **۳. تعیین سیگنال خرید/فروش**
df["Target"] = np.where(df["Close"].shift(-1) > df["Close"], 1, 0)

# 📌 **۴. آماده‌سازی داده‌ها**
features = ["SMA_20", "SMA_50", "RSI", "Volatility"]
df.dropna(inplace=True)
X = df[features]
y = df["Target"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 📌 **۵. آموزش مدل `Random Forest`**
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 📌 **۶. پیش‌بینی و ارزیابی مدل**
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy:.2f}")

# 📌 **۷. اجرای استراتژی**
df["Prediction"] = model.predict(X)
df["Strategy Returns"] = df["Prediction"].shift(1) * df["Close"].pct_change()

# 📌 **۸. محاسبه سود و زیان استراتژی**
cumulative_returns = (1 + df["Strategy Returns"]).cumprod()
print(f"📊 Final Portfolio Value: {cumulative_returns.iloc[-1]:.2f}")

# 📌 **۹. ذخیره داده‌های پردازش‌شده برای بررسی‌های بعدی**
df.to_csv("/Users/rezaghasemi/Downloads/Programming/Quantitative/AAPL_ML_Strategy.csv")
print(f"📈 Mean Daily Return: {df['Strategy Returns'].mean():.5f}")
print(f"📅 Number of Trading Days: {len(df)}")
print(f"📊 Cumulative Returns: {cumulative_returns.iloc[-1]:.2f}")

buy_and_hold_returns = (df["Close"].iloc[-1] / df["Close"].iloc[0])
print(f"📊 Buy & Hold Returns: {buy_and_hold_returns:.2f}")


import matplotlib.pyplot as plt

plt.figure(figsize=(10,5))
plt.plot(cumulative_returns, label="Strategy Returns", color="blue")
plt.axhline(y=1, color='gray', linestyle='--', label="Initial Capital")
plt.legend()
plt.title("Cumulative Strategy Returns")
plt.show()

# 📌 **۵. پیش‌بینی معاملات و سیگنال‌ها**
df["Buy Signal"] = (df["Prediction"] == 1)  # خرید
df["Sell Signal"] = (df["Prediction"] == 0)  # فروش

# 📌 **۶. نمایش خرید و فروش روی نمودار قیمت**
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["Close"], label="Close Price", color="blue", alpha=0.6)

# نمایش نقاط خرید 📈
plt.scatter(df.index[df["Buy Signal"]], df["Close"][df["Buy Signal"]], 
            marker="^", color="green", label="Buy Signal", alpha=1, s=100)

# نمایش نقاط فروش 📉
plt.scatter(df.index[df["Sell Signal"]], df["Close"][df["Sell Signal"]], 
            marker="v", color="red", label="Sell Signal", alpha=1, s=100)

plt.title("Trading Strategy (RandomForest)")
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.legend()
plt.grid()
plt.show()

