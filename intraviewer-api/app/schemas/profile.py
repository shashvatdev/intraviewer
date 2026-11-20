from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.validators import (
    clean_name,
    normalize_phone,
    normalize_url,
    optional_text,
)


class EducationItem(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_year: Optional[int] = Field(default=None, ge=1950, le=2100)
    end_year: Optional[int] = Field(default=None, ge=1950, le=2100)

    @field_validator("institution")
    @classmethod
    def _inst(cls, v: str) -> str:
        return clean_name(v, "Institution", min_len=2, max_len=150)

    @field_validator("degree", "field_of_study")
    @classmethod
    def _opt(cls, v: Optional[str]) -> Optional[str]:
        return optional_text(v, 120, "This field")

    @model_validator(mode="after")
    def _years(self):
        if self.start_year and self.end_year and self.end_year < self.start_year:
            raise ValueError("End year can't be before start year")
        return self


class ExperienceItem(BaseModel):
    company: str
    title: str
    start_date: Optional[str] = None  # YYYY-MM
    end_date: Optional[str] = None  # YYYY-MM
    current: bool = False
    description: Optional[str] = None

    @field_validator("company")
    @classmethod
    def _company(cls, v: str) -> str:
        return clean_name(v, "Company", min_len=1, max_len=150)

    @field_validator("title")
    @classmethod
    def _title(cls, v: str) -> str:
        return clean_name(v, "Title", min_len=1, max_len=150)

    @field_validator("start_date", "end_date")
    @classmethod
    def _month(cls, v: Optional[str]) -> Optional[str]:
        if v is None or not v.strip():
            return None
        v = v.strip()
        import re

        if not re.match(r"^\d{4}-(0[1-9]|1[0-2])$", v):
            raise ValueError("Use the format YYYY-MM")
        return v

    @field_validator("description")
    @classmethod
    def _desc(cls, v: Optional[str]) -> Optional[str]:
        return optional_text(v, 1000, "Description")

    @model_validator(mode="after")
    def _dates(self):
        if self.current:
            self.end_date = None
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValueError("End date can't be before start date")
        return self


class CandidateProfileUpdate(BaseModel):
    """Partial update: only fields present in the request body are changed."""

    name: Optional[str] = None
    phone: Optional[str] = None
    skills: Optional[List[str]] = None
    education: Optional[List[EducationItem]] = None
    experience: Optional[List[ExperienceItem]] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    @field_validator("name")
    @classmethod
    def _name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return clean_name(v, "Full name")

    @field_validator("phone")
    @classmethod
    def _phone(cls, v: Optional[str]) -> Optional[str]:
        return normalize_phone(v)

    @field_validator("skills")
    @classmethod
    def _skills(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        seen, out = set(), []
        for s in v:
            s = " ".join(str(s).split())
            if not s:
                continue
            if len(s) > 50:
                raise ValueError("Each skill must be at most 50 characters")
            if s.lower() not in seen:
                seen.add(s.lower())
                out.append(s)
        if len(out) > 50:
            raise ValueError("You can add up to 50 skills")
        return out

    @field_validator("education", "experience")
    @classmethod
    def _max_items(cls, v):
        if v is not None and len(v) > 20:
            raise ValueError("You can add up to 20 entries")
        return v

    @field_validator("github_url")
    @classmethod
    def _gh(cls, v: Optional[str]) -> Optional[str]:
        return normalize_url(v, "GitHub URL", allowed_hosts=["github.com"])

    @field_validator("linkedin_url")
    @classmethod
    def _li(cls, v: Optional[str]) -> Optional[str]:
        return normalize_url(v, "LinkedIn URL", allowed_hosts=["linkedin.com"])

    @field_validator("portfolio_url")
    @classmethod
    def _pf(cls, v: Optional[str]) -> Optional[str]:
        return normalize_url(v, "portfolio URL")


class CompanyProfileUpdate(BaseModel):
    """Partial update: only fields present in the request body are changed."""

    company_name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

    @field_validator("company_name")
    @classmethod
    def _name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            raise ValueError("Company name is required")
        return clean_name(v, "Company name", max_len=120)

    @field_validator("website")
    @classmethod
    def _site(cls, v: Optional[str]) -> Optional[str]:
        return normalize_url(v, "website URL")

    @field_validator("industry")
    @classmethod
    def _industry(cls, v: Optional[str]) -> Optional[str]:
        return optional_text(v, 120, "Industry")

    @field_validator("description")
    @classmethod
    def _desc(cls, v: Optional[str]) -> Optional[str]:
        return optional_text(v, 2000, "Description")

    @field_validator("location")
    @classmethod
    def _loc(cls, v: Optional[str]) -> Optional[str]:
        return optional_text(v, 120, "Location")
