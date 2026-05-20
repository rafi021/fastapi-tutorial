from fastapi import FastAPI


app = FastAPI()

# Products with 20 items
products = [f"Product {i}" for i in range(1, 21)]


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


# Create new Product
@app.post("/products")
def create_product(name: str):
    new_product = f"Product {len(products) + 1}: {name}"
    products.append(new_product)
    return {"message": "Product created", "product": new_product}