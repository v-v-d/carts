from pydantic import BaseModel


class UserDataOutputDTO(BaseModel):
    id: int
