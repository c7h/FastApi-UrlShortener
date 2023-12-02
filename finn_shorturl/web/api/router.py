from fastapi.routing import APIRouter

from finn_shorturl.web.api import monitoring, shortener

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(shortener.router)
