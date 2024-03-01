import requests
# from alpaca.trading.client import TradingClient

# account_id = "1a859566-ce53-4e12-8a5b-5691623b4c80"

# url = f"http://broker-api.sandbox.alpaca.markets/v2/broker/accounts/{account_id}/account/portfolio/history"
# # url = f"https://broker-api.sandbox.alpaca.markets/v1/trading/accounts/{account_id}/account/portfolio/history"

# headers = {
#     "accept": "application/json",
#     "content-type": "application/json",
#     "authorization": "Basic YXBwLmRldi50b21AZ21haWwuY29tOkAyKl5GclBxI2s1dUp3MDhBekVeSFFyWUA2YSZmdUh2"
# }

# response = requests.get(url, headers=headers)

# print(response.text)

# tradingAPI = TradingClient("PKTDA1H78SMZ901NCS9B", "AUL76yVZj1S9DsfpCiRrpMxISDUulBqehE160MRy", paper=True)

# acc = tradingAPI.get_account()

# print(acc)
# print(dir(acc))

api_key = "30148276ZkHSVLNUjGfwCocXdidhGWuqpuFJF"


url = "https://demo.trading212.com/api/v0/equity/orders/market"

payload = {
  "quantity": 0.1,
  "ticker": "AAPL_US_EQ"
}

headers = {
  "Content-Type": "application/json",
  "Authorization": api_key
}

response = requests.post(url, json=payload, headers=headers)

data = response.json()
print(data)




url = "https://demo.trading212.com/api/v0/equity/orders"

headers = {"Authorization": api_key}

response = requests.get(url, headers=headers)

data = response.json()
print(data)