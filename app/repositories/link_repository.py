import json
import logging
import os
import threading
from pathlib import Path
from typing import Optional

from app.models import Link

logger = logging.getLogger(__name__)


class LinkRepository:
    def __init__(self, data_file: str = "data/links.json"):
        self._lock = threading.RLock()
        self._links: dict[str, Link] = {}
        self._short_codes: dict[str, str] = {}
        self._data_file = Path(data_file)
        self._ensure_data_dir()
        self._load()

    def _ensure_data_dir(self):
        self._data_file.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        if self._data_file.exists():
            try:
                with open(self._data_file, "r") as f:
                    data = json.load(f)
                    for link_data in data.get("links", {}).values():
                        link = Link.from_dict(link_data)
                        self._links[link.id] = link
                        self._short_codes[link.short_code] = link.id
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Failed to load links data: {e}")

    def _save(self):
        self._ensure_data_dir()
        backup_file = self._data_file.with_suffix(".json.bak")
        if self._data_file.exists():
            self._data_file.rename(backup_file)
        data = {"links": {link.id: link.to_dict() for link in self._links.values()}}
        with open(self._data_file, "w") as f:
            json.dump(data, f, indent=2)
        if backup_file.exists():
            backup_file.unlink()

    def create(self, link: Link) -> Link:
        with self._lock:
            self._links[link.id] = link
            self._short_codes[link.short_code] = link.id
            self._save()
        return link

    def get_by_short_code(self, short_code: str) -> Optional[Link]:
        with self._lock:
            link_id = self._short_codes.get(short_code)
            if link_id:
                return self._links.get(link_id)
            return None

    def get_by_id(self, link_id: str) -> Optional[Link]:
        with self._lock:
            return self._links.get(link_id)

    def delete(self, short_code: str) -> bool:
        with self._lock:
            link_id = self._short_codes.get(short_code)
            if link_id and link_id in self._links:
                del self._links[link_id]
                del self._short_codes[short_code]
                self._save()
                return True
            return False

    def increment_clicks(self, short_code: str) -> Optional[Link]:
        with self._lock:
            link_id = self._short_codes.get(short_code)
            if link_id and link_id in self._links:
                self._links[link_id].clicks += 1
                link = self._links[link_id]
                self._save()
                return link
            return None

    def short_code_exists(self, short_code: str) -> bool:
        with self._lock:
            return short_code in self._short_codes

    def get_all(self) -> list[Link]:
        with self._lock:
            return list(self._links.values())
