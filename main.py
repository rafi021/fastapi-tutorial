from fastapi import FastAPI


app = FastAPI()

@app.get("/products")
def get_products():
    return {"products": ["Product 1", "Product 2", "Product 3"]}


# Dynamic route to get a specific product by ID (path parameter)
@app.get("/products/{product_id}")
def get_product(product_id: int):
    return {"product_id": product_id, "name": f"Product {product_id}"}


@app.get("/products-by-slug/{product_slug}")
def get_product_by_slug(product_slug: str):
    return {"product_slug": product_slug, "name": f"Product {product_slug}"}