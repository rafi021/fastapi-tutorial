from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Products with name, price, stock --> add 20 items
products = [
    {"name": f"Product {i}", "price": i * 10.0, "stock": i * 5}
    for i in range(1, 21)
]

class CreateProductRequest (BaseModel):
    name: str
    price: float
    stock: int



# Query Parameters ---> optional params (search, sort) --> limit (default value)
# Multiple query params
@app.get("/products")
def get_products(search: str = None, limit: int = 10, sort: str = None):
    filtered_products = products
    if search:
        filtered_products = [p for p in filtered_products if search.lower() in p.lower()]
    if sort:
        filtered_products.sort(key=lambda x: x.lower() if sort == "asc" else -x.lower())
    return {"products": filtered_products[:limit]}


# Create new Product with pydantic validation
@app.post("/products")
def create_product(product: CreateProductRequest):
    new_product = {
        "name": product.name,
        "price": product.price,
        "stock": product.stock
    }
    products.append(new_product)
    return {"message": "Product created", "product": new_product}