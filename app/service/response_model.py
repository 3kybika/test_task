from pydantic import BaseModel


class MessageResponseModel(BaseModel):
    message: str
