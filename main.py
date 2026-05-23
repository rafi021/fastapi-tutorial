from fastapi import FastAPI, HTTPException, Depends, Header
from jose import jwt, JWTError
from datetime import datetime,timezone, timedelta


app = FastAPI()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create Token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Verify Token
def verify_token(token: str = Header(None)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid or Expired token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or Expired token")

# Login API (Token Generate)
@app.post("/login")
def login(username: str, password: str):
    if username != "admin" or password != "123456":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}


# Protected API
@app.get("/protected")
def protected_route(username: str = Depends(verify_token)):
    return {"message": f"Hello, {username}. This is a protected route!"}