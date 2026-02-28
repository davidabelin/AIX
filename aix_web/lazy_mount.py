"""Lazy WSGI app loader for mount-on-first-request behavior."""

from __future__ import annotations

from threading import RLock
from typing import Callable


class LazyMountApp:
    """Load a target WSGI app only when the first request arrives."""

    def __init__(self, *, name: str, loader: Callable[[], Callable]) -> None:
        self.name = str(name)
        self._loader = loader
        self._app = None
        self._error: str | None = None
        self._lock = RLock()

    @property
    def loaded(self) -> bool:
        """Return ``True`` when the wrapped app has been loaded."""

        return self._app is not None

    @property
    def error(self) -> str | None:
        """Return the latest load error, when present."""

        return self._error

    def _load(self):
        if self._app is not None or self._error is not None:
            return self._app
        with self._lock:
            if self._app is not None or self._error is not None:
                return self._app
            try:
                self._app = self._loader()
            except Exception as exc:  # pragma: no cover
                self._error = str(exc)
        return self._app

    def __call__(self, environ, start_response):
        app = self._load()
        if app is None:
            body = f"Lab '{self.name}' is unavailable: {self._error or 'unknown error'}\n".encode("utf-8")
            headers = [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", str(len(body))),
            ]
            start_response("503 SERVICE UNAVAILABLE", headers)
            return [body]
        return app(environ, start_response)

