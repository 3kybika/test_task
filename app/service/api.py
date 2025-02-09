from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.service.auth_service import AuthService, UserExistsException
from app.service.request_model import UserDataRequestModel
from app.service.response_model import MessageResponseModel


auth_router = APIRouter(tags=["auth"])

"""
POST /signup

Request:
{ "email": "user@example.com", "password": "password123" }
Response:
{ "message": "User registered successfully" }
"""


@auth_router.post(
    "/signup",
    response_model=MessageResponseModel,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": MessageResponseModel,
            "message": "User registered successfully",
        },
        status.HTTP_409_CONFLICT: {
            "model": MessageResponseModel,
            "message": "User with such email already exists",
        },
    },
)
async def sign_up(
    response: Response,
    user_data: UserDataRequestModel,
    service: AuthService = Depends(),
):
    """
    Create a new account

    **user_data**: username, email and password for registration
    """
    try:
        await service.register_new_user(user_data.email, user_data.password)

    except UserExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    return MessageResponseModel(message="User registered successfully")
