from fastapi import APIRouter

from app.api.blueprints import router as blueprints_router
from app.api.runs import router as runs_router

router = APIRouter()
router.include_router(blueprints_router)
router.include_router(runs_router)
