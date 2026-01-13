from __future__ import annotations

from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter, SimpleSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


def init_otel(
    *,
    app: object,
    enabled: bool,
    service_name: str,
    otlp_endpoint: Optional[str],
    console_exporter: bool,
    sample_rate: float,
) -> None:
    if not enabled:
        return

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource, sampler=TraceIdRatioBased(sample_rate))

    if console_exporter:
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    if otlp_endpoint:
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))

    trace.set_tracer_provider(provider)

    # Auto-instrument inbound HTTP + outbound httpx
    FastAPIInstrumentor.instrument_app(app)  # type: ignore[arg-type]
    HTTPXClientInstrumentor().instrument()


def get_tracer() -> trace.Tracer:
    return trace.get_tracer("examsmith")
