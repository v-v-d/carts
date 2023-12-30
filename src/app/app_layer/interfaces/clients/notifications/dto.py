from pydantic import BaseModel


class SendNotificationInputDTO(BaseModel):
    user_id: int
    text: str
