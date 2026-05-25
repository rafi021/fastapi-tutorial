# import requests
# from bs4 import BeautifulSoup

# url = "https://www.example.com"

# response = requests.get(url)

# soup = BeautifulSoup(response.text, 'html.parser')

# print(soup.title.text)

from time import time

from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup


app = FastAPI()

# Cache Storage
cache_data = []
last_fetch = 0

@app.get("/scrape")
def scrape(page: int = 1, limit: int = 10):
    global cache_data, last_fetch
    # Check if cache is valid (e.g., 10 minutes)

    start = time()
    if time() - last_fetch > 60:
        print("Fetching new data...")
        url = "https://www.dailyamardesh.com"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cache_data = []
        for item in soup.find_all('span', class_='inline'):
            cache_data.append(item.text.strip())
        last_fetch = time()
    else:
        print("Using cached data...")

    end = time()
    print(f"Time taken: {end - start} seconds")
    return {
        "total": len(cache_data),
        "news": cache_data
    }