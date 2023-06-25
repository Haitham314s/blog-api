import os
from datetime import datetime, timedelta
from typing import Dict

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from .schemas import TokenData, db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(payload: Dict):
    to_encode = payload.copy()
    expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expiration_time})

    return jwt.encode(to_encode, key=SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if not id:
            raise credential_exception

        return TokenData(id=id)
    except JWTError:
        raise credential_exception


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token could not be verified or is expired",
        headers={"WWW-AUTHENTICATE": "Bearer"},
    )
    current_user_id = verify_access_token(token, credential_exception).id

    return await db["users"].find_one({"_id": current_user_id})
