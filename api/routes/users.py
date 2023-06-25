import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from ..oauth2 import get_current_user
from ..schemas import User, UserResponse, db
from ..send_email import send_registration_mail
from ..utils import get_password_hash

router = APIRouter(prefix="/users", tags=["User Routes"])


@router.post(
    "/registration",
    response_description="Register a user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def registration(user_info: User):
    user_info = jsonable_encoder(user_info)

    # Check for duplicates
    username_found = await db["users"].find_one({"name": user_info["name"]})
    email_found = await db["users"].find_one({"email": user_info["email"]})

    if username_found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username is already taken"
        )

    if email_found:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )

    # Hash user password
    user_info["password"] = get_password_hash(user_info["password"])

    # Create api key
    user_info["apiKey"] = secrets.token_hex(20)

    new_user = await db["users"].insert_one(user_info)
    created_user = await db["users"].find_one({"_id": new_user.inserted_id})

    # TODO: Change email provider to SendGrid or use less secure email user
    # await send_registration_mail(
    #     "Registration Successful",
    #     user_info["email"],
    #     {"title": "Registration Successful", "name": user_info["name"]},
    # )

    return created_user


@router.post(
    "/details", response_description="Get user details", response_model=UserResponse
)
async def details(current_user=Depends(get_current_user)):
    return await db["users"].find_one({"_id": current_user["_id"]})
