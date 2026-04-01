from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.dependencies import get_service
from app.schemas import LinkCreate, LinkResponse, LinkDetail, LinkStats, LinkDelete


def is_link_expired(link) -> bool:
    if link.expires_at is None:
        return False
    return datetime.now(link.expires_at.tzinfo) > link.expires_at


router = APIRouter(prefix="/api/links", tags=["links"])


@router.post("", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
def create_link(
    link_data: LinkCreate,
    service=Depends(get_service),
    request: Request = None,
):
    try:
        link = service.create_link(
            original_url=str(link_data.url),
            expires_at=link_data.expires_at,
            custom_code=link_data.custom_code,
        )
        base_url = str(request.base_url).rstrip("/") if request else ""
        return LinkResponse(
            short_code=link.short_code,
            original_url=link.original_url,
            short_url=f"{base_url}/{link.short_code}",
            created_at=link.created_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{short_code}", response_model=LinkDetail)
def get_link(
    short_code: str,
    service=Depends(get_service),
    request: Request = None,
):
    link = service.get_link(short_code)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    if is_link_expired(link):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Link has expired")
    base_url = str(request.base_url).rstrip("/") if request else ""
    return LinkDetail(
        id=link.id,
        short_code=link.short_code,
        original_url=link.original_url,
        short_url=f"{base_url}/{link.short_code}",
        created_at=link.created_at,
        clicks=link.clicks,
        expires_at=link.expires_at,
    )


@router.delete("/{short_code}", response_model=LinkDelete)
def delete_link(short_code: str, service=Depends(get_service)):
    deleted = service.delete_link(short_code)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    return LinkDelete(deleted=True, short_code=short_code)


@router.get("/{short_code}/stats", response_model=LinkStats)
def get_stats(short_code: str, service=Depends(get_service)):
    link = service.get_stats(short_code)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Link not found"
        )
    if is_link_expired(link):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Link has expired")
    return LinkStats(
        short_code=link.short_code,
        original_url=link.original_url,
        clicks=link.clicks,
        created_at=link.created_at,
        expires_at=link.expires_at,
    )
