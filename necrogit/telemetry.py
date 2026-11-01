import os
from contextlib import contextmanager
from typing import Generator, Any, Optional, Dict
import sentry_sdk

def init_telemetry() -> None:
    """Initializes Sentry Agent Tracing if SENTRY_DSN is present in the environment."""
    dsn = os.getenv("SENTRY_DSN")
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            release="necrogit@0.1.0",
            environment=os.getenv("NECROGIT_ENV", "production"),
            _experiments={
                "continuous_profiling_auto_start": False,
            }
        )

def _is_sentry_active() -> bool:
    """Check if Sentry SDK is active without triggering deprecation warnings."""
    if hasattr(sentry_sdk, "is_initialized"):
        return sentry_sdk.is_initialized()
    hub = getattr(sentry_sdk, "Hub", None)
    return hub is not None and getattr(hub.current, "client", None) is not None

def record_breadcrumb(category: str, message: str, level: str = "info", data: Optional[Dict[str, Any]] = None) -> None:
    """Record an agent reasoning step or archaeology breadcrumb in Sentry."""
    if _is_sentry_active():
        sentry_sdk.add_breadcrumb(
            category=category,
            message=message,
            level=level,
            data=data or {}
        )

def set_agent_context(agent_name: str, details: Dict[str, Any]) -> None:
    """Attach structured agent telemetry and maintainer persona context to Sentry trace scope."""
    if _is_sentry_active():
        sentry_sdk.set_context(agent_name, details)

@contextmanager
def trace_span(op: str, description: str, data: Optional[Dict[str, Any]] = None) -> Generator[Any, None, None]:
    """Context manager for fine-grained Sentry Agent Tracing spans with attributes."""
    if _is_sentry_active():
        with sentry_sdk.start_span(op=op, description=description) as span:
            if data:
                for k, v in data.items():
                    try:
                        span.set_data(k, v)
                    except Exception:
                        pass
            yield span
    else:
        yield None
