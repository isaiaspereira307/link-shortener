import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional

from app.models import Link
from app.repositories.link_repository import LinkRepository


class LinkService:
    BASE62_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    def __init__(self, repository: LinkRepository):
        self._repository = repository

    def _generate_short_code(
        self, original_url: str, custom_code: Optional[str] = None
    ) -> str:
        if custom_code:
            if self._repository.short_code_exists(custom_code):
                raise ValueError("Custom code already exists")
            return custom_code

        for _ in range(10):
            timestamp = str(datetime.now(timezone.utc).timestamp())
            hash_input = f"{original_url}{timestamp}{secrets.token_hex(4)}"
            hash_bytes = hashlib.sha256(hash_input.encode()).digest()
            code = self._base62_encode(hash_bytes)[:8]
            if not self._repository.short_code_exists(code):
                return code

        raise ValueError("Failed to generate unique short code")

    def _base62_encode(self, data: bytes) -> str:
        num = int.from_bytes(data, "big")
        if num == 0:
            return self.BASE62_CHARS[0]
        result = []
        while num > 0:
            num, remainder = divmod(num, 62)
            result.append(self.BASE62_CHARS[remainder])
        return "".join(reversed(result))

    def create_link(
        self,
        original_url: str,
        expires_at: Optional[datetime] = None,
        custom_code: Optional[str] = None,
    ) -> Link:
        short_code = self._generate_short_code(original_url, custom_code)
        link = Link(
            short_code=short_code, original_url=original_url, expires_at=expires_at
        )
        return self._repository.create(link)

    def get_link(self, short_code: str) -> Optional[Link]:
        return self._repository.get_by_short_code(short_code)

    def delete_link(self, short_code: str) -> bool:
        return self._repository.delete(short_code)

    def track_click(self, short_code: str) -> Optional[Link]:
        return self._repository.increment_clicks(short_code)

    def get_stats(self, short_code: str) -> Optional[Link]:
        return self._repository.get_by_short_code(short_code)
