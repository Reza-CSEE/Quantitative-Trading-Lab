import time
import requests

# 🔹 API Endpoints
BINANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
COINBASE_API = "https://api.coinbase.com/v2/prices/BTC-USD/spot"


# 🔹 Trading Configurations
SPREAD_THRESHOLD = 10  # Minimum price difference for arbitrage execution
TRADE_AMOUNT = 0.01  # BTC amount for each trade

# 🔹 Virtual Trading Balance
balance = {"BTC": 0, "USDT": 10000}  # Starting balance of $10,000


def get_price():
    """Fetches BTC price from Binance and Coinbase"""
    binance_price = float(requests.get(BINANCE_API).json()["price"])
    coinbase_price = float(requests.get(COINBASE_API).json()["data"]["amount"])
    return binance_price, coinbase_price


def get_fees():
    """Fetches trading fees from Binance and Coinbase"""
    binance_fee = 0.1 / 100  # Default maker/taker fee (0.1%)
    coinbase_fee = 0.5 / 100  # Default fee (0.5%)

    return binance_fee, coinbase_fee


def execute_trade(action, exchange, price, fee):
    """Executes a simulated trade with transaction fees"""
    global balance
    cost = TRADE_AMOUNT * price
    fee_cost = cost * fee
    net_cost = cost + fee_cost if action == "buy" else cost - fee_cost

    if action == "buy" and balance["USDT"] >= net_cost:
        balance["USDT"] -= net_cost
        balance["BTC"] += TRADE_AMOUNT
        print(f"✅ BUY {TRADE_AMOUNT} BTC from {exchange} at {price:.2f} (Fee: {fee_cost:.2f})")
    elif action == "sell" and balance["BTC"] >= TRADE_AMOUNT:
        balance["BTC"] -= TRADE_AMOUNT
        balance["USDT"] += net_cost
        print(f"✅ SELL {TRADE_AMOUNT} BTC on {exchange} at {price:.2f} (Fee: {fee_cost:.2f})")
    else:
        print("❌ Insufficient balance!")


def arbitrage_trading():
    """Runs arbitrage strategy continuously"""
    while True:
        binance_price, coinbase_price = get_price()
        binance_fee, coinbase_fee = get_fees()
        spread = abs(binance_price - coinbase_price)

        print(f"💰 Binance: {binance_price:.2f} | Coinbase: {coinbase_price:.2f} | Spread: {spread:.2f}")

        if spread >= SPREAD_THRESHOLD:
            if binance_price < coinbase_price:
                profit = (coinbase_price - binance_price) * TRADE_AMOUNT - (
                    binance_price * TRADE_AMOUNT * binance_fee + coinbase_price * TRADE_AMOUNT * coinbase_fee
                )
                print(f"Binance_fee = {binance_fee}")
                print(f"Coinbase_fee = {coinbase_fee}")
                print(f"Profit: {profit:.2f}")
                if profit > 0:
                    execute_trade("buy", "Binance", binance_price, binance_fee)
                    execute_trade("sell", "Coinbase", coinbase_price, coinbase_fee)
                    print(f"💰 Net Profit: {profit:.2f} USD after fees")
                else:
                    print("⚠️ No profitable arbitrage opportunity after fees.")
            else:
                profit = (binance_price - coinbase_price) * TRADE_AMOUNT - (
                    coinbase_price * TRADE_AMOUNT * coinbase_fee + binance_price * TRADE_AMOUNT * binance_fee
                )
                print(f"Binance_fee = {binance_fee}")
                print(f"Coinbase_fee = {coinbase_fee}")
                print(f"Profit: {profit:.2f}")
                if profit > 0:
                    execute_trade("buy", "Coinbase", coinbase_price, coinbase_fee)
                    execute_trade("sell", "Binance", binance_price, binance_fee)
                    print(f"💰 Net Profit: {profit:.2f} USD after fees")
                else:
                    print("⚠️ No profitable arbitrage opportunity after fees.")

        print(f"💵 Balance: {balance}")
        time.sleep(2)  # Runs every 2 seconds


# 🚀 Run Arbitrage Trading Strategy
arbitrage_trading()
