from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str | None = None
    household_size: int = 1
    city: str | None = None
    has_car: bool = True

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str | None
    household_size: int
    plan: str
    has_car: bool
    city: str | None

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
