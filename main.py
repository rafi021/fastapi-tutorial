import requests

response = requests.get('https://fakestoreapi.com/products')

if response.status_code == 200:
    print(response.json())
else:
    print("Failed to retrieve data")