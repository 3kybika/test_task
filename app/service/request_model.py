from pydantic import BaseModel


class UserDataRequestModel(BaseModel):
    email: str
    password: str
