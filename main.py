# import requests
# from bs4 import BeautifulSoup

# url = "https://www.example.com"

# response = requests.get(url)

# soup = BeautifulSoup(response.text, 'html.parser')

# print(soup.title.text)

from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup


app = FastAPI()

@app.get("/scrape")
def scrape(page: int = 1, limit: int = 10):
    url = "https://www.dailyamardesh.com"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = []
    for item in soup.find_all('span', class_='inline'):
        title.append(item.text.strip())

    # Pagination logic
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "limit": limit,
        "total": len(title),
        "news": title[start:end]
    } 