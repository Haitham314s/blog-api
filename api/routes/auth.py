from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .. import utils
from ..oauth2 import create_access_token
from ..schemas import Token, db

router = APIRouter(prefix="/login", tags=["Authentication"])


@router.post("", response_model=Token, status_code=status.HTTP_200_OK)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends()):
    user = await db["users"].find_one({"name": user_credentials.username})
    if user is None:
        user = await db["users"].find_one({"email": user_credentials.username})

    if user and utils.verify_password(user_credentials.password, user["password"]):
        access_token = create_access_token(payload={"id": user["_id"]})

        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user credentials"
        )
