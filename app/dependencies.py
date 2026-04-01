from app.repositories import LinkRepository
from app.services import LinkService

_repository: LinkRepository | None = None


def get_repository() -> LinkRepository:
    global _repository
    if _repository is None:
        _repository = LinkRepository()
    return _repository


def get_service() -> LinkService:
    return LinkService(get_repository())
