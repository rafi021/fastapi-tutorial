from fastapi import FastAPI


app = FastAPI()

@app.get("/products")
def get_products():
    return {"products": ["Product 1", "Product 2", "Product 3"]}


# Dynamic route to get a specific product by ID (path parameter)
@app.get("/products/{product_id}")
def get_product(product_id: int):
    return {"product_id": product_id, "name": f"Product {product_id}"}