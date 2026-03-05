"""WSGI path-prefix wrapper used for API compatibility aliases."""

from __future__ import annotations


class PathPrefixWrapper:
    """Prepend a path prefix before dispatching to another WSGI app."""

    def __init__(self, app, *, prefix: str) -> None:
        self._app = app
        self._prefix = "/" + str(prefix).strip("/")

    @property
    def loaded(self) -> bool:
        return bool(getattr(self._app, "loaded", False))

    @property
    def error(self) -> str | None:
        return getattr(self._app, "error", None)

    def __call__(self, environ, start_response):
        env = dict(environ)
        path_info = str(env.get("PATH_INFO", "") or "")
        if not path_info.startswith(self._prefix):
            if path_info in {"", "/"}:
                path_info = self._prefix
            elif path_info.startswith("/"):
                path_info = f"{self._prefix}{path_info}"
            else:
                path_info = f"{self._prefix}/{path_info}"
            env["PATH_INFO"] = path_info
        return self._app(env, start_response)
