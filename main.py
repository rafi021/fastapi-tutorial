from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, World!"}

@app.get("/about")
def about():
    return {"message": "This is the about page."}

@app.get("/contact")
def contact():
    contact = {
        "email": "contact@example.com",
        "phone": "01111111111111"
    }
    return {
        "status": "success",
        "message": "Contact us at contact@example.com",
        "data": contact
    }