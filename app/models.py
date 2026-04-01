from datetime import datetime, timezone
from typing import Optional
import uuid


class Link:
    def __init__(
        self,
        short_code: str,
        original_url: str,
        id: Optional[str] = None,
        clicks: int = 0,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.short_code = short_code
        self.original_url = original_url
        self.clicks = clicks
        self.created_at = created_at or datetime.now(timezone.utc)
        self.expires_at = expires_at

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "short_code": self.short_code,
            "original_url": self.original_url,
            "clicks": self.clicks,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Link":
        return cls(
            id=data["id"],
            short_code=data["short_code"],
            original_url=data["original_url"],
            clicks=data.get("clicks", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None,
        )
