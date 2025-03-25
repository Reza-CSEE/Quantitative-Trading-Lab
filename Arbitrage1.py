import time
import requests
import numpy as np

# 📌 تنظیمات
BINANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
COINBASE_API = "https://api.coinbase.com/v2/prices/BTC-USD/spot"

SPREAD_THRESHOLD = 10  # حداقل اختلاف قیمت برای اجرای آربیتراژ
TRADE_AMOUNT = 0.01  # مقدار بیت‌کوین برای معامله (مثال)

# 📊 اطلاعات خرید و فروش
balance = {"BTC": 0, "USDT": 10000}  # سرمایه اولیه 10000 دلار


def get_price():
    """دریافت قیمت BTC از دو صرافی"""
    binance_price = float(requests.get(BINANCE_API).json()["price"])
    coinbase_price = float(requests.get(COINBASE_API).json()["data"]["amount"])
    return binance_price, coinbase_price


def execute_trade(action, exchange, price):
    """اجرای معامله (شبیه‌سازی)"""
    global balance
    if action == "buy":
        cost = TRADE_AMOUNT * price
        if balance["USDT"] >= cost:
            balance["USDT"] -= cost
            balance["BTC"] += TRADE_AMOUNT
            print(f"✅ Buy {TRADE_AMOUNT} BTC from {exchange} price: {price:.2f}")
        else:
            print("❌ You do not have enough USDT!")
    elif action == "sell":
        if balance["BTC"] >= TRADE_AMOUNT:
            balance["BTC"] -= TRADE_AMOUNT
            balance["USDT"] += TRADE_AMOUNT * price
            print(f"✅ Sell {TRADE_AMOUNT} BTC in {exchange} price: {price:.2f}")
        else:
            print("❌ You do not have enough BTC!")


def arbitrage_trading():
    """اجرای استراتژی آربیتراژ به‌صورت پیوسته"""
    while True:
        binance_price, coinbase_price = get_price()
        spread = abs(binance_price - coinbase_price)

        print(f"💰 Binance: {binance_price:.2f} | Coinbase: {coinbase_price:.2f} | Spread: {spread:.2f}")
        
        if spread >= SPREAD_THRESHOLD:
            if binance_price < coinbase_price:
                execute_trade("buy", "Binance", binance_price)
                execute_trade("sell", "Coinbase", coinbase_price)
            else:
                execute_trade("buy", "Coinbase", coinbase_price)
                execute_trade("sell", "Binance", binance_price)
        
        print(f"💵 Balance: {balance}")
        time.sleep(2)  # ⏳ اجرای هر 2 ثانیه


# 🚀 اجرای استراتژی آربیتراژ
arbitrage_trading()
