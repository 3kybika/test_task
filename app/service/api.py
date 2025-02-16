import logging
from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.service.auth_service import AuthService, UserExistsException
from app.service.request_model import UserDataRequestModel
from app.service.response_model import MessageResponseModel, MessageTokenResponseModel


auth_router = APIRouter(tags=["auth"])

logger = logging.getLogger("AuthApi")

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
    logger.debug("sign_up")
    try:
        await service.register_new_user(user_data.email, user_data.password)

    except UserExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    return MessageResponseModel(message="User registered successfully")



"""
POST /login

Request:
{ "email": "user@example.com", "password": "password123" }
Response:
{ "token": "jwt-token" }
"""
@auth_router.post(
    "/login",
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
async def login(
    response: Response,
    user_data: UserDataRequestModel,
    service: AuthService = Depends(),
):
    """
    Create a new account

    **user_data**: username, email and password for registration
    """
    logger.debug("sign_up")
    try:
        token = await service.login(user_data.email, user_data.password)

    except UserExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    return MessageTokenResponseModel(message=token)