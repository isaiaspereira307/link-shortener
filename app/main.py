from contextlib import asynccontextmanager
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.dependencies import get_repository
from app.routes import router as links_router


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        now = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip] if now - ts < self.window
        ]

        if not self.requests[client_ip]:
            del self.requests[client_ip]

        if (
            client_ip in self.requests
            and len(self.requests[client_ip]) >= self.max_requests
        ):
            return JSONResponse(
                status_code=429, content={"detail": "Too many requests"}
            )

        self.requests[client_ip].append(now)
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_repository()
    yield


app = FastAPI(
    title="Link Shortener API",
    description="High-performance URL shortener service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


from datetime import datetime


def is_link_expired(link) -> bool:
    if link.expires_at is None:
        return False
    return datetime.now(link.expires_at.tzinfo) > link.expires_at


def is_safe_redirect_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


@app.get("/{short_code}")
async def redirect_to_url(short_code: str):
    reserved_routes = {"docs", "redoc", "health", "openapi.json", "api", "links"}
    if short_code in reserved_routes:
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    repository = get_repository()
    link = repository.get_by_short_code(short_code)
    if not link:
        return JSONResponse(
            status_code=404, content={"detail": f"Link not found: {short_code}"}
        )

    if is_link_expired(link):
        return JSONResponse(status_code=410, content={"detail": "Link has expired"})

    if not is_safe_redirect_url(link.original_url):
        return JSONResponse(status_code=400, content={"detail": "Invalid redirect URL"})

    repository.increment_clicks(short_code)
    return RedirectResponse(url=link.original_url, status_code=307)


app.include_router(links_router)
