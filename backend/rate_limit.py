from collections.abc import Callable
from typing import Any


class _NoopLimiter:
    def limit(self, _limit_value: str) -> Callable:
        def decorator(func: Callable) -> Callable:
            return func

        return decorator


try:
    from slowapi import Limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    from slowapi.util import get_remote_address
    from slowapi import _rate_limit_exceeded_handler

    limiter: Any = Limiter(key_func=get_remote_address)
    SLOWAPI_AVAILABLE = True
except ImportError:
    limiter = _NoopLimiter()
    SLOWAPI_AVAILABLE = False


def install_rate_limiter(app: Any) -> None:
    if not SLOWAPI_AVAILABLE:
        return

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
