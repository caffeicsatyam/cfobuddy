import requests
api = 'SAMD340RX0TYOMMI'

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol=IBM&apikey={api}'
r = requests.get(url)
data = r.json()

print(data)