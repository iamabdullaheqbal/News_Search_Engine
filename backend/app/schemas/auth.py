import re

from pydantic import BaseModel, EmailStr, Field, field_validator


_PASSWORD_MIN = 12
_PASSWORD_MAX_BYTES = 72
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$"
)


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=_PASSWORD_MIN, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v.encode("utf-8")) > _PASSWORD_MAX_BYTES:
            raise ValueError("Password is too long (max 72 bytes)")
        if not _PASSWORD_PATTERN.match(v):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one digit"
            )
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    email: str
    name: str | None = None
    interests: list[str] = []

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    user: UserOut


class InterestToggleRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=100)


class SetInterestsRequest(BaseModel):
    topics: list[str] = Field(max_length=20)


class FollowsRequest(BaseModel):
    topics: list[str] = Field(max_length=20)
