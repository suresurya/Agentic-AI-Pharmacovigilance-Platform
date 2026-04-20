from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException
from jose import jwt
from pydantic import BaseModel
from app.config import settings

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    officer_id: str
    email: str


@router.post("/token", response_model=TokenResponse)
async def login(payload: LoginRequest):
    if (
        payload.email != settings.demo_officer_email
        or payload.password != settings.demo_officer_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    token_data = {"sub": payload.email, "officer_id": "demo-officer", "exp": expire}
    token = jwt.encode(token_data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    return TokenResponse(access_token=token, officer_id="demo-officer", email=payload.email)
