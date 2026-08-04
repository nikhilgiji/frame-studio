from fastapi import APIRouter

from app.api.routes.exports import router as exports_router
from app.api.routes.extraction import router as extraction_router
from app.api.routes.frames import router as frames_router
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router
from app.api.routes.integrity import router as integrity_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.projects import router as projects_router
from app.api.routes.queues import router as queues_router
from app.api.routes.review import router as review_router
from app.api.routes.statistics import router as statistics_router
from app.api.routes.videos import router as videos_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(projects_router)
api_router.include_router(videos_router)
api_router.include_router(extraction_router)
api_router.include_router(frames_router)
api_router.include_router(review_router)
api_router.include_router(queues_router)
api_router.include_router(statistics_router)
api_router.include_router(jobs_router)
api_router.include_router(history_router)
api_router.include_router(integrity_router)
api_router.include_router(exports_router)
