import os
from contextlib import contextmanager
from typing import Generator, Any
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
        )

def _is_sentry_active() -> bool:
    """Check if Sentry SDK is active without triggering deprecation warnings."""
    if hasattr(sentry_sdk, "is_initialized"):
        return sentry_sdk.is_initialized()
    hub = getattr(sentry_sdk, "Hub", None)
    return hub is not None and getattr(hub.current, "client", None) is not None

@contextmanager
def trace_span(op: str, description: str) -> Generator[Any, None, None]:
    """Context manager for Sentry span tracing with fallback when unconfigured."""
    if _is_sentry_active():
        with sentry_sdk.start_span(op=op, description=description) as span:
            yield span
    else:
        yield None
