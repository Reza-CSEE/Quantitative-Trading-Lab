import requests
import pandas as pd

api_key = "#####################"  # Insert your API Key
STOCK = "AAPL"
EXCHANGE = "US"  # بازار آمریکا
START_DATE = "2024-01-01"
END_DATE = "2024-12-30"

url = f"https://eodhistoricaldata.com/api/eod/{STOCK}.{EXCHANGE}?from={START_DATE}&to={END_DATE}&api_token={API_KEY}&fmt=json"

response = requests.get(url)

# بررسی وضعیت HTTP
if response.status_code == 200:
    try:
        data = response.json()
        df = pd.DataFrame(data)
        df.to_csv(f"{STOCK}_data.csv")
        print(df.head())
    except Exception as e:
        print(f"Error decoding JSON: {e}")
else:
    print(f"Error: API request failed with status code {response.status_code}")
    print("Response text:", response.text)  # نمایش متن پاسخ برای بررسی مشکل
