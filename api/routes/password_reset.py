from fastapi import APIRouter, HTTPException, status

from ..oauth2 import create_access_token, get_current_user
from ..schemas import NewPassword, PasswordReset, db
from ..send_email import password_reset
from ..utils import get_password_hash

router = APIRouter(prefix="/password", tags=["Password Reset"])


@router.post("/request", response_description="Reset user password")
async def reset_request(user_email: PasswordReset):
    user = await db["users"].find_one({"email": user_email.email})
    print(user)
    if user is not None:
        token = create_access_token({"id": user["_id"]})
        reset_link = f"http://localhost:8001/reset?token={token}"

        # Send email
        await password_reset(
            "Password Reset",
            user["email"],
            {"title": "Password Reset", "name": user["name"], "reset_link": reset_link},
        )
        return {
            "message": "Email has been sent with instructions to reset your password"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {user_email.email} not found",
        )


@router.put("/reset", response_description="Reset password")
async def reset(token: str, new_password: NewPassword):
    request_data = {k: v for k, v in new_password.dict().items() if v is not None}
    request_data["password"] = get_password_hash(request_data["password"])

    if len(request_data) >= 1:
        user = await get_current_user(token)
        update_result = await db["users"].update_one(
            {"_id": user["_id"]}, {"$set": request_data}
        )

        if update_result.modified_count == 1:
            updated_user = await db["users"].find_one({"_id": user["_id"]})
            if updated_user is not None:
                return updated_user

        existing_user = await db["users"].find_one({"_id": user["_id"]})
        if existing_user is not None:
            return existing_user

        # Raise error when user not found
        return HTTPException(status_code=404, detail="User not found")
