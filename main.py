from fastapi import FastAPI, Request
from time import time

app = FastAPI()

@app.middleware("http")
async def loggerMiddleware(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    duration = time() - start_time
    print(f"Request Path: {request.url.path} | completed in {duration} seconds")
    return response

@app.get("/")
async def root():
    return {"message": "Hello World"}