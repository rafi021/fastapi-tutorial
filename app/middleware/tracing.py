from opentelemetry import trace
from opentelemetry.propagate import extract
from opentelemetry.trace import SpanKind, Status, StatusCode
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import trace_id_ctx_var


class TracingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str) -> None:
        super().__init__(app)
        self.tracer = trace.get_tracer(service_name)

    async def dispatch(self, request, call_next):
        context = extract(dict(request.headers))

        with self.tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            context=context,
            kind=SpanKind.SERVER,
        ) as span:
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.target", request.url.path)

            trace_id = format(span.get_span_context().trace_id, "032x")
            request.state.trace_id = trace_id
            trace_id_token = trace_id_ctx_var.set(trace_id)

            try:
                response = await call_next(request)
                span.set_attribute("http.status_code", response.status_code)
                if response.status_code >= 500:
                    span.set_status(Status(StatusCode.ERROR))
                response.headers["X-Trace-ID"] = trace_id
                return response
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR))
                raise
            finally:
                trace_id_ctx_var.reset(trace_id_token)
