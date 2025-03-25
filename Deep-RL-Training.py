import requests
import gym
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from gym import spaces
from datetime import datetime, timedelta


# 📌 **تنظیمات**
TICKER = "AAPL"
api_key = "#####################"  # Insert your API Key

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

# 📌 **۱. تعریف محیط معاملاتی**
class TradingEnv(gym.Env):
    def __init__(self, df):
        super(TradingEnv, self).__init__()
        self.df = df.reset_index()
        self.current_step = 0
        self.cash = 10000  # مقدار اولیه سرمایه
        self.shares = 0  # تعداد سهام خریداری‌شده
        self.total_value = self.cash
        
        # **تعریف فضای وضعیت** (ویژگی‌های بازار)
        #self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(len(df.columns) - 1,), dtype=np.float32)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)

        
        # **تعریف فضای عمل** (۰ = نگه‌داری، ۱ = خرید، ۲ = فروش)
        self.action_space = spaces.Discrete(3)
    
    def reset(self):
        self.current_step = 0
        self.cash = 10000
        self.shares = 0
        self.total_value = self.cash
        return self._next_observation()
    
    def _next_observation(self):
        return self.df.iloc[self.current_step, 1:].values.astype(np.float32)
    
    def step(self, action):
        # **بررسی اینکه آیا ستون `date` موجود است**
        if 'date' in self.df.columns:
            current_date = self.df.iloc[self.current_step]['date']
        else:
            current_date = self.df.index[self.current_step]  # اگر حذف شده باشد، از `index` استفاده کن

        current_price = self.df.iloc[self.current_step]['Close']
        
        reward = 0
        
        if action == 1 and self.cash >= current_price:
            # خرید سهام
            self.shares = self.cash // current_price
            self.cash -= self.shares * current_price
            print(f"📈 Buy at {current_price:.2f} on {current_date}")

        elif action == 2 and self.shares > 0:
            # فروش سهام
            self.cash += self.shares * current_price
            self.shares = 0
            print(f"📉 Sell at {current_price:.2f} on {current_date}")

        self.total_value = self.cash + (self.shares * current_price)
        reward = self.total_value - 10000  # میزان سود به عنوان پاداش
        self.current_step += 1
        done = self.current_step >= len(self.df) - 1
        return self._next_observation(), reward, done, {}

    def render(self, mode='human'):
        print(f'Step: {self.current_step}, Cash: {self.cash:.2f}, Shares: {self.shares}, Total Value: {self.total_value:.2f}')
# 📌 **۲. آماده‌سازی داده‌های بازار**
#df = pd.read_csv("/Users/rezaghasemi/Downloads/Programming/Quantitative/AAPL.csv")  # جایگزین با مسیر داده‌های واقعی

df['SMA_10'] = df['Close'].rolling(window=10).mean()
df['SMA_50'] = df['Close'].rolling(window=50).mean()
df['RSI'] = np.random.uniform(30, 70, len(df))  # نمونه‌سازی مقدار RSI

df.dropna(inplace=True)
df = df[['Close', 'SMA_10', 'SMA_50', 'RSI']]  # انتخاب ویژگی‌های بازار


# 📌 **۳. ایجاد محیط و آموزش مدل DRL**
train_env = DummyVecEnv([lambda: TradingEnv(df)])
model = PPO("MlpPolicy", train_env, verbose=1)
model.learn(total_timesteps=10000)


# 📌 **۴. تست استراتژی روی داده‌های واقعی و ذخیره نقاط خرید و فروش**
test_env = TradingEnv(df)
obs = test_env.reset()
done = False
total_rewards = 0

# لیست ذخیره خرید و فروش
buy_signals = []
sell_signals = []

print(test_env.df.head())  # بررسی ساختار داده‌ها


while not done:
    action, _ = model.predict(obs)
    obs, reward, done, _ = test_env.step(action)
    total_rewards += reward
    
    # ثبت نقاط خرید
    if action == 1 and test_env.cash >= test_env.df.iloc[test_env.current_step]['Close']:
        buy_signals.append((test_env.df.iloc[test_env.current_step]['date'], test_env.df.iloc[test_env.current_step]['Close']))
    
    # ثبت نقاط فروش
    elif action == 2 and test_env.shares > 0:
        sell_signals.append((test_env.df.iloc[test_env.current_step]['date'], test_env.df.iloc[test_env.current_step]['Close']))
    
    test_env.render()


print(f'📊 **Final Portfolio Value: {test_env.total_value:.2f} USD**')


# نمایش نقاط خرید و فروش روی نمودار
buy_dates, buy_prices = zip(*buy_signals) if buy_signals else ([], [])
sell_dates, sell_prices = zip(*sell_signals) if sell_signals else ([], [])


plt.scatter(buy_dates, buy_prices, label="Buy Signal", marker="^", color="green", s=100, edgecolors="black", linewidth=1.5)
plt.scatter(sell_dates, sell_prices, label="Sell Signal", marker="v", color="red", s=100, edgecolors="black", linewidth=1.5)

# 📌 **۵. نمایش سوددهی در نمودار**
plt.plot(df.index, df['Close'], label="Stock Price", color='black')
plt.xlabel("Time")
plt.ylabel("Stock Price")
plt.title("Deep Reinforcement Learning Trading Strategy")
plt.legend()
plt.show()
