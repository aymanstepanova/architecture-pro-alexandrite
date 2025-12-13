import os
import httpx
from fastapi import FastAPI

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "service-a")
SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8080/")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://simplest-collector.observability:4318")

# --- OpenTelemetry Tracing setup ---
resource = Resource.create({"service.name": SERVICE_NAME})

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

provider.add_span_processor(
    BatchSpanProcessor(
        OTLPSpanExporter(endpoint=f"{OTLP_ENDPOINT}/v1/traces")
    )
)

# --- FastAPI app + instrumentation ---
app = FastAPI()

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()


@app.get("/")
async def root():
    """
    1) Приходит запрос в service-a
    2) service-a вызывает service-b
    3) благодаря httpx-инструментатору контекст трассы автоматически
       прокидывается в заголовках (traceparent), и вызов попадает в один trace.
    """
    async with httpx.AsyncClient(timeout=5.0) as client:
        r = await client.get(SERVICE_B_URL)
        r.raise_for_status()
        downstream = r.json()

    return {"service": "a", "downstream": downstream}
