from pydantic import BaseModel

class TokenRefreshRequest(BaseModel):
    refresh_token: str

class TokenRefreshResponse(BaseModel):
    access_token: str
    refresh_token: str

class LogoutResponse(BaseModel):
    message: str
