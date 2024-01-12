from pydantic import BaseModel
from datetime import datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenInDB(BaseModel):
    id: int
    status: bool
    time_created: datetime
    user_id: int



class User(BaseModel):
    username: str
    email: str or None = None

    class Config:
        orm_mode = True

class UserCreate(User):
    password: str

class UserInDB(UserCreate):
    id: int
    disabled: bool or None = False
    time_created: datetime
    time_updated: datetime

    class Config:
        orm_mode = True



class Measurement(BaseModel):
    temperature: float

class MeasurementInDB(Measurement):
    id: int
    time_created: datetime
    time_updated: datetime
    device_id: int

    class Config:
        orm_mode = True


class Device(BaseModel):
    name: str

class DeviceInDB(Device):
    id: int
    time_created: datetime
    time_updated: datetime
    user_id: int

    class Config:
        orm_mode = True
