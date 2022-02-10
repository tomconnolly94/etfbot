import requests
import os
from dotenv import load_dotenv

load_dotenv()

MARKETSTACK_API_KEY = os.getenv('MARKETSTACK_API_KEY')

params = {
  'access_key': MARKETSTACK_API_KEY
}

api_result = requests.get('http://api.marketstack.com/v1/tickers/aapl/eod', params)

api_response = api_result.json()

print(api_response)

for stock_data in api_response['data']:
    print(f"Ticker {stock_data['symbol']} has a day high of {stock_data['high']} on {stock_data['date']}")