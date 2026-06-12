import bcrypt as _bcrypt
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings

def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password[:72].encode('utf-8'), _bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _bcrypt.checkpw(plain_password[:72].encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=7)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
