from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from app.core.email_domains import is_consumer_email
from app.schemas.validators import clean_name, normalize_email, validate_password_strength

RoleLiteral = Literal["CANDIDATE", "COMPANY"]
PurposeLiteral = Literal["EMAIL_VERIFICATION", "PASSWORD_RESET"]


class _PasswordConfirmMixin(BaseModel):
    password: str
    confirm_password: str

    @field_validator("password")
    @classmethod
    def _strong(cls, v: str) -> str:
        return validate_password_strength(v)

    @model_validator(mode="after")
    def _match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class CandidateRegisterRequest(_PasswordConfirmMixin):
    name: str
    email: EmailStr

    @field_validator("name")
    @classmethod
    def _name(cls, v: str) -> str:
        return clean_name(v, "Full name")

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return normalize_email(v)


class CompanyRegisterRequest(_PasswordConfirmMixin):
    company_name: str
    email: EmailStr

    @field_validator("company_name")
    @classmethod
    def _company(cls, v: str) -> str:
        return clean_name(v, "Company name", max_len=120)

    @field_validator("email")
    @classmethod
    def _business_email(cls, v: str) -> str:
        v = normalize_email(v)
        if is_consumer_email(v):
            raise ValueError(
                "Please use your work email. Personal email providers aren't accepted for company accounts."
            )
        return v


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str
    purpose: PurposeLiteral

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return normalize_email(v)

    @field_validator("otp")
    @classmethod
    def _otp(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Enter the 6-digit code")
        return v


class ResendOtpRequest(BaseModel):
    email: EmailStr
    purpose: PurposeLiteral

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return normalize_email(v)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: RoleLiteral

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return normalize_email(v)

    @field_validator("password")
    @classmethod
    def _pw(cls, v: str) -> str:
        if not v:
            raise ValueError("Password is required")
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        return normalize_email(v)


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def _strong(cls, v: str) -> str:
        return validate_password_strength(v)

    @model_validator(mode="after")
    def _match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self
