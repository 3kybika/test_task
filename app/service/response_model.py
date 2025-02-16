from pydantic import BaseModel


class MessageResponseModel(BaseModel):
    message: str

class MessageTokenResponseModel(BaseModel):
    token: str