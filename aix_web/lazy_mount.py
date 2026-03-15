"""Lazy WSGI app loader for mount-on-first-request behavior.

Role
----
Provide the mount-on-first-request behavior that lets the AIX hub advertise
multiple labs without importing or initializing every sibling application at
process start.

Cross-Repo Context
------------------
This is one of the core pieces that makes the AIX umbrella model work locally:
lab adapters register loaders, the registry wraps them in ``LazyMountApp``, and
the AIX dispatcher mounts those wrappers under the relevant path prefixes.
"""

from __future__ import annotations

from threading import RLock
from typing import Callable


class LazyMountApp:
    """Load a target WSGI app only when the first request arrives.

    Role
    ----
    Delay expensive imports and app-factory setup until a request actually hits
    the mounted lab path.

    Depends On
    ----------
    A callable loader that returns a WSGI-compatible application object.

    Used By
    -------
    ``aix_web.lab_registry.resolve_lab_mounts`` and ultimately
    ``aix_web.create_app``.

    Notes
    -----
    The wrapper caches either the loaded app or the first load error so repeat
    requests remain deterministic and cheap.
    """

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
        """Load the target app exactly once and cache either app or error.

        Role
        ----
        Centralize the thread-safe "first hit wins" behavior for lazy lab
        loading.
        """

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
        """Dispatch one request to the lazily loaded target app.

        Returns a ``503`` text response when the target lab failed to load.
        """

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
