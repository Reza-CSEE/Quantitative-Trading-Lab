import time
import requests

# 🔹 List of Top 10 Cryptocurrencies (Including BTC)
CRYPTO_LIST = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOGE", "DOT", "LTC", "MATIC", "SHIB"]

# 🔹 API Endpoints
BINANCE_API_TEMPLATE = "https://api.binance.com/api/v3/ticker/price?symbol={}USDT"
#The price of MATIC on Binance is wrong and it doesn't update.
COINBASE_API_TEMPLATE = "https://api.coinbase.com/v2/prices/{}-USD/spot"

# 🔹 Trading Configurations
#SPREAD_THRESHOLD = 10  # Minimum price difference for arbitrage execution
#TRADE_AMOUNT = 0.01  # Amount of each cryptocurrency for trading (example)

# 🔹 Virtual Trading Balance
balance = {crypto: 0 for crypto in CRYPTO_LIST}
balance["USDT"] = 10000  # Starting balance of $10,000


def get_price(crypto):
    """Fetches cryptocurrency prices from Binance and Coinbase"""
    binance_url = BINANCE_API_TEMPLATE.format(crypto)
    coinbase_url = COINBASE_API_TEMPLATE.format(crypto)

    try:
        binance_price = float(requests.get(binance_url).json()["price"])
        coinbase_price = float(requests.get(coinbase_url).json()["data"]["amount"])
        return binance_price, coinbase_price
    except Exception as e:
        print(f"❌ Error fetching price for {crypto}: {e}")
        return None, None


def get_fees():
    """Fetches trading fees from Binance and Coinbase"""
    binance_fee = 0.1 / 100  # Default maker/taker fee (0.1%)
    coinbase_fee = 0.5 / 100  # Default fee (0.5%)
    return binance_fee, coinbase_fee


def execute_trade(action, exchange, crypto, price, fee):
    """Executes a simulated trade with transaction fees"""
    global balance
    binance_price, coinbase_price = get_price(crypto)
    TRADE_AMOUNT = max(0.01, 100 / binance_price) 
    cost = TRADE_AMOUNT * price
    fee_cost = cost * fee
    net_cost = cost + fee_cost if action == "buy" else cost - fee_cost

    if action == "buy" and balance["USDT"] >= net_cost:
        balance["USDT"] -= net_cost
        balance[crypto] += TRADE_AMOUNT
        print(f"✅ BUY {TRADE_AMOUNT} {crypto} from {exchange} at {price:.2f} (Fee: {fee_cost:.2f})")
    elif action == "sell" and balance[crypto] >= TRADE_AMOUNT:
        balance[crypto] -= TRADE_AMOUNT
        balance["USDT"] += net_cost
        print(f"✅ SELL {TRADE_AMOUNT} {crypto} on {exchange} at {price:.2f} (Fee: {fee_cost:.2f})")
    else:
        print(f"❌ Insufficient balance for {crypto}!")


def arbitrage_trading():
    """Runs arbitrage strategy continuously for all selected cryptocurrencies"""
    while True:
        for crypto in CRYPTO_LIST:
            binance_price, coinbase_price = get_price(crypto)
            SPREAD_THRESHOLD = binance_price * 0.002  # 0.2% of the coin price as the threshold
            TRADE_AMOUNT = max(0.01, 100 / binance_price)  # Ensures reasonable trade amount

            if binance_price is None or coinbase_price is None:
                continue  # Skip if unable to fetch price

            binance_fee, coinbase_fee = get_fees()
            spread = abs(binance_price - coinbase_price)

            print(f"💰 {crypto}: Binance {binance_price:.2f} | Coinbase {coinbase_price:.2f} | Spread: {spread:.2f}")

            if spread >= SPREAD_THRESHOLD:
                if binance_price < coinbase_price:
                    profit = (coinbase_price - binance_price) * TRADE_AMOUNT - (
                        binance_price * TRADE_AMOUNT * binance_fee + coinbase_price * TRADE_AMOUNT * coinbase_fee
                    )
                    if profit > 0:
                        execute_trade("buy", "Binance", crypto, binance_price, binance_fee)
                        execute_trade("sell", "Coinbase", crypto, coinbase_price, coinbase_fee)
                        print(f"💰 Net Profit for {crypto}: {profit:.2f} USD after fees")
                    else:
                        print(f"Profit: {profit:.2f}")
                        print(f"⚠️ No profitable arbitrage opportunity for {crypto} after fees.")
                else:
                    profit = (binance_price - coinbase_price) * TRADE_AMOUNT - (
                        coinbase_price * TRADE_AMOUNT * coinbase_fee + binance_price * TRADE_AMOUNT * binance_fee
                    )
                    if profit > 0:
                        execute_trade("buy", "Coinbase", crypto, coinbase_price, coinbase_fee)
                        execute_trade("sell", "Binance", crypto, binance_price, binance_fee)
                        print(f"💰 Net Profit for {crypto}: {profit:.2f} USD after fees")
                    else:
                        print(f"Profit: {profit:.2f}")
                        print(f"⚠️ No profitable arbitrage opportunity for {crypto} after fees.")

        print(f"💵 Balance: {balance}")
        time.sleep(2)  # Runs every 2 seconds


# 🚀 Run Arbitrage Trading Strategy
arbitrage_trading()
