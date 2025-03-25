import requests
import pandas as pd

url = f"https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2023-01-09/2024-12-10?adjusted=true&sort=asc&apiKey=BCnibG6TFwiypPXLQW6cqy5cdcLAP0bf"

response = requests.get(url)

# بررسی وضعیت HTTP
if response.status_code == 200:
    try:
        data = response.json()
        df = pd.DataFrame(data)
        df.to_csv(f"/Users/rezaghasemi/Downloads/Programming/Quantitative/AAPL_data.csv")
        print(df.head())
    except Exception as e:
        print(f"Error decoding JSON: {e}")
else:
    print(f"Error: API request failed with status code {response.status_code}")
    print("Response text:", response.text)  # نمایش متن پاسخ برای بررسی مشکل
