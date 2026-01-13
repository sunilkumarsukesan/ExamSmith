from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "ExamSmith Orchestrator"
    env: str = "dev"
    cors_origins: str = "http://localhost:3000"

    storage_backend: str = "inmemory"  # inmemory|mongo
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "examsmith"

    auto_process_runs: bool = False
    max_worker_concurrency: int = 4
    max_auto_regen_attempts: int = 1
    default_eval_threshold: float = 0.85

    # Default LLM selection (can be overridden per run via RunConfig)
    default_llm_provider: str = "openai"
    default_llm_model: str = "gpt-4o-mini"
    default_llm_temperature: float = 0.2
    default_llm_top_p: float = 1.0
    default_llm_max_output_tokens: int = 800

    # Optional provider credentials (kept generic; adapters read env too)
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    anthropic_api_key: str | None = None
    anthropic_base_url: str | None = None
    anthropic_version: str | None = None

    groq_api_key: str | None = None
    groq_base_url: str | None = None

    # Observability (OpenTelemetry)
    observability_enabled: bool = True
    otel_service_name: str = "examsmith-orchestrator"
    otel_exporter_otlp_endpoint: str | None = None
    otel_exporter_console: bool = False
    otel_sample_rate: float = 0.1


settings = Settings()
