# import requests

# response = requests.get('https://fakestoreapi.com/products')

# if response.status_code == 200:
#     print(response.json())
# else:
#     print("Failed to retrieve data")

from fastapi import FastAPI
import requests

app = FastAPI()

# GET ALL Data
@app.get("/products")
def get_products():
    url = 'https://fakestoreapi.com/products'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve data"}