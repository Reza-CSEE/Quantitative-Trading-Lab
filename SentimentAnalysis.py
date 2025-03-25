import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from textblob import TextBlob
from datetime import datetime, timedelta

# 📌 **تنظیمات**
TICKER = "AAPL"
API_KEY = "BCnibG6TFwiypPXLQW6cqy5cdcLAP0bf"

EXCEL_FILENAME = "/Users/rezaghasemi/Downloads/Programming/Quantitative/Sentiment_Trading_Data.xlsx"

# 📌 **📊 دریافت داده‌های تاریخی از Polygon.io**
start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')

url = f"https://api.polygon.io/v2/aggs/ticker/{TICKER}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc&apiKey={API_KEY}"
response = requests.get(url)
data = response.json()

# 📌 **ایجاد DataFrame برای داده‌های قیمتی**
df = pd.DataFrame(data.get('results', []))
if df.empty:
    print("⚠️ No stock data received from Polygon.io.")
    exit()

df['date'] = pd.to_datetime(df['t'], unit='ms').dt.date
df.rename(columns={'c': 'Close', 'v': 'Volume'}, inplace=True)
df = df[['date', 'Close', 'Volume']]

print("📊 Stock Data Loaded:")
print(df.head())

# 📌 **📥 دریافت اخبار از Polygon.io**
news_url = f"https://api.polygon.io/v2/reference/news?ticker={TICKER}&limit=1000&apiKey={API_KEY}"
news_response = requests.get(news_url)
news_data = news_response.json()

# 📌 **بررسی خطا در دریافت اخبار**
if 'results' not in news_data:
    print("⚠️ Error: No 'results' found in Polygon News API response. Here is the response:")
    print(news_data)
    exit()

for i, article in enumerate(news_data.get("results", [])[:5]):  # نمایش فقط 5 خبر اول
    print(f" News {i+1}:")
    print(f"📰Title: {article.get('title')}")
    print(f"📅 date: {article.get('published_utc')}")
    print(f"🔗 Link: {article.get('article_url')}")
    print("-" * 50)


# 📌 **تحلیل احساسات اخبار**
news_list = []
for article in news_data['results']:
    news_date = datetime.strptime(article['published_utc'], "%Y-%m-%dT%H:%M:%SZ").date()
    sentiment_score = TextBlob(article['title']).sentiment.polarity
    news_list.append({"date": news_date, "Sentiment": sentiment_score})

# 📌 **ایجاد DataFrame برای اخبار**
news_df = pd.DataFrame(news_list)
news_df["date"] = pd.to_datetime(news_df["date"]).dt.date

# 📌 **ادغام اخبار با داده‌های قیمتی**
news_sentiment = news_df.groupby("date")["Sentiment"].mean().reset_index()
df = df.merge(news_sentiment, on="date", how="left")
df["Sentiment"].fillna(0, inplace=True)

print("📊 Merged Data Loaded:")
print(df.head())

# 📌 **📈 تعیین سیگنال خرید و فروش بر اساس احساسات**
df["Signal"] = np.where(df["Sentiment"] > 0.1, 1, np.where(df["Sentiment"] < -0.1, -1, 0))


# **📌 جلوگیری از خرید مجدد در حین داشتن معامله باز**
position_open = False  # بررسی وضعیت معامله باز
buy_price = 0
sell_price = 0
profits = []
df["Trade"] = ""  # مقداردهی اولیه برای جلوگیری از NaN

for i in range(1, len(df)):  # از i=1 شروع می‌کنیم تا مقدار قبلی را چک کنیم
    prev_trade = df.loc[i-1, "Trade"]  # بررسی آخرین معامله انجام‌شده

    # **📈 ورود به معامله خرید (فقط اگر معامله باز نباشد و قبلاً خرید انجام نشده باشد)**
    if df.loc[i, "Signal"] == 1 and not position_open and prev_trade != "Buy":
        df.loc[i, "Trade"] = "Buy"
        buy_price = df.loc[i, "Close"]
        position_open = True  # **پرچم باز بودن معامله را تنظیم می‌کنیم**
        print(f"📈 Buy at {buy_price:.2f} on {df.index[i]}")
        continue  # 🚀 جلوگیری از ورود به فروش در همان روز

    # **📉 خروج از معامله (فقط اگر معامله باز باشد و سیگنال فروش داده شود)**
    if df.loc[i, "Signal"] == -1 and position_open:
        df.loc[i, "Trade"] = "Sell"
        sell_price = df.loc[i, "Close"]
        profits.append(sell_price - buy_price)  # ✅ ثبت سود معامله
        position_open = False  # **بستن معامله**
        print(f"📉 Sell at {sell_price:.2f} on {df.index[i]}, Profit: {sell_price - buy_price:.2f} USD")
        continue  # 🚀 جلوگیری از ورود به خرید در همان روز

# **🔹 نمایش مجموع سودها**
total_profit = sum(profits)
print(f"💰 Total Profit: {total_profit:.2f} USD")




# 📌 **📊 ذخیره داده‌ها در یک فایل Excel**
with pd.ExcelWriter(EXCEL_FILENAME) as writer:
    df.to_excel(writer, sheet_name="Stock Data", index=False)
    news_df.to_excel(writer, sheet_name="News Data", index=False)

print(f"📥 Data saved to {EXCEL_FILENAME}")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# **📌 اطمینان از اینکه ستون تاریخ، DateTime است**
df["date"] = pd.to_datetime(df["date"])
df.set_index("date", inplace=True)  # **تنظیم `date` به‌عنوان index برای ترسیم بهتر**

# **📊 نمایش نمودار قیمت با نقاط خرید و فروش**
plt.figure(figsize=(12, 6))
plt.plot(df.index, df["Close"], label="Stock Price", color='black', alpha=0.7)

# **📌 نمایش نقاط خرید و فروش روی نمودار**
buy_signals = df[df["Trade"] == "Buy"]
sell_signals = df[df["Trade"] == "Sell"]

plt.scatter(buy_signals.index, buy_signals["Close"], label="Buy Signal", marker="^", color="green", s=100, edgecolors="black", linewidth=1.5)
plt.scatter(sell_signals.index, sell_signals["Close"], label="Sell Signal", marker="v", color="red", s=100, edgecolors="black", linewidth=1.5)

# **📌 تنظیمات اضافی برای خوانایی بهتر**
plt.xlabel("Date")
plt.ylabel("Stock Price")
plt.title(f"📊 Sentiment Analysis Trading Strategy for {TICKER}")
plt.legend()

# **📌 فرمت تاریخ در محور X**
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())

# **📌 نمایش Grid برای خوانایی بهتر**
plt.grid(True, linestyle="--", alpha=0.5)

# **📌 نمایش نمودار**
plt.show()
