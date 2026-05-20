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
    category: CategoryRequest

# CategoryRequest name required but description is optional
class CategoryRequest (BaseModel):
    name: str
    description: str | None = None


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