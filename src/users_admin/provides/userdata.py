from pydantic import BaseModel


class Userdata(BaseModel):
    provider: str
    provider_user_id: str
    provider_unique_id: str
    email: str
    name: str
    avatar_url: str


