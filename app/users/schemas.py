from pydantic import BaseModel, EmailStr, Field, UUID4, ConfigDict
from uuid import UUID


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    user_uuid: UUID4
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class PublicUser(BaseModel):
    user_uuid: UUID
    name: str
    model_config = ConfigDict(from_attributes=True)


class LoginData(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    user_uuid: UUID
    access_token: str
