import logging
import stat
import typing
from collections.abc import Awaitable, Callable, MutableMapping
from sys import path

from common.logging import get_logger
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, DispatchFunction
from starlette.types import ASGIApp

for _log in ["uvicorn", "uvicorn.error"]:
    # Make sure the logs are handled by the root logger
    logging.getLogger(_log).handlers.clear()
    logging.getLogger(_log).propagate = True

# Uvicorn logs are re-emitted with more context. We effectively silence them here
logging.getLogger("uvicorn.access").handlers.clear()
logging.getLogger("uvicorn.access").propagate = False


class FastAPILoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle logging for FastAPI applications.
    This middleware ensures that all requests and responses are logged.
    """

    def __init__(
        self,
        app: Callable[
            [
                MutableMapping[str, typing.Any],
                Callable[[], Awaitable[MutableMapping[str, typing.Any]]],
                Callable[[MutableMapping[str, typing.Any]], Awaitable[None]],
            ],
            Awaitable[None],
        ],
        dispatch: (
            Callable[
                [Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]
            ]
            | None
        ) = None,
    ) -> None:
        super().__init__(app, dispatch)
        self.logger = get_logger(__name__)

    async def dispatch(
        self,
        request: Request,
        call_next: typing.Callable[[Request], typing.Awaitable[Response]],
    ) -> Response:
        response = await call_next(request)
        self.logger.info(
            "request",
            status_code=response.status_code,
            method=request.method,
            path=request.url.path,
        )

        return response
