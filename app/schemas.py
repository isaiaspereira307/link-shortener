from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, field_validator


class LinkCreate(BaseModel):
    url: HttpUrl = Field(..., description="URL to shorten")
    expires_at: Optional[datetime] = Field(None, description="Expiration datetime")
    custom_code: Optional[str] = Field(
        None, min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9]+$"
    )

    @field_validator("url", mode="before")
    @classmethod
    def validate_url(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("URL cannot be empty")
            if v.startswith(("javascript:", "data:", "blob:")):
                raise ValueError("Invalid URL scheme")
            if not v.startswith(("http://", "https://")):
                if v.startswith("//"):
                    v = "https:" + v
                elif v.startswith("/"):
                    pass
                else:
                    v = "https://" + v
        return v


class LinkResponse(BaseModel):
    short_code: str
    original_url: str
    short_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LinkDetail(LinkResponse):
    id: str
    clicks: int
    expires_at: Optional[datetime] = None


class LinkStats(BaseModel):
    short_code: str
    original_url: str
    clicks: int
    created_at: datetime
    expires_at: Optional[datetime] = None


class LinkDelete(BaseModel):
    deleted: bool
    short_code: str
