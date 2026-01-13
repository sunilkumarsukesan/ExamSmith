from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.observability import init_otel
from app.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    init_otel(
        app=app,
        enabled=settings.observability_enabled,
        service_name=settings.otel_service_name,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
        console_exporter=settings.otel_exporter_console,
        sample_rate=settings.otel_sample_rate,
    )

    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "env": settings.env}

    return app


app = create_app()
