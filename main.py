from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from passlib.context import CryptContext
import os
from datetime import timedelta
from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

app = FastAPI()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0b3lvZnJhbmNlQGdtYWlsLmNvbSIsImF1ZCI6IkFsbCBBZGRyZXNzZXMiLCJpc3MiOiJodHRwczovL2xvY2FsaG9zdDo4MDgwLyIsImV4cCI6MTY3MjU2Njg4MCwiaWF0IjoxNjcyNTYyMjgwLCJqdGkiOiI4ODk1OTg1NzQxMjA4NzE5MjA3In0.gP4sJ76Hq6f8B7O1WQ5QHwM61uZ0o6r6e8Kv3p3Kl8Y")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

jwt_config = {
    "secret_key": SECRET_KEY,
    "algorithm": ALGORITHM,
    "access_token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
}
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class RegisterUser(BaseModel):
    username: str
    password: str

class User(BaseModel):
    username = str
    hashed_password = str
    name = str
    role = int

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)




fake_users_db = {}

@app.post("/register")
async def register(user: User):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    hashed_password = get_password_hash(user.password)
    user_data = user.dict()
    user_data["password"] = hashed_password
    fake_users_db[user.username] = user_data

    return {"message": "User registered successfully"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = jwt_config["access_token_expire_minutes"]
    expire_time = datetime.utcnow() + timedelta(minutes=expire)
    to_encode.update({"exp": expire_time})
    encoded_jwt = jwt.encode(to_encode, jwt_config["secret_key"], algorithm=jwt_config["algorithm"])
    return encoded_jwt

@app.post("/login")
async def login(user: User):
    user_data = fake_users_db.get(user.username)
    if not user_data or not verify_password(user.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=jwt_config["access_token_expire_minutes"])
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer", "expires_in": int(access_token_expires.total_seconds())}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)