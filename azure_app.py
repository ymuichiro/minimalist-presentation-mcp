from __future__ import annotations

import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any, Awaitable, Callable


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from example.communication_compiler.main import create_app as create_demo_app  # noqa: E402
from minimalist_presentation_mcp.mcp.server import create_mcp_server_from_settings  # noqa: E402


Scope = dict[str, Any]
Receive = Callable[[], Awaitable[dict[str, Any]]]
Send = Callable[[dict[str, Any]], Awaitable[None]]


class AzureDemoApp:
    """Dispatch the demo UI and MCP server from one App Service process."""

    def __init__(self) -> None:
        self.demo_app = create_demo_app()
        self.mcp_app = create_mcp_server_from_settings().streamable_http_app()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self._lifespan(receive, send)
            return

        path = str(scope.get("path") or "/")
        if _is_demo_path(path):
            await self.demo_app(scope, receive, send)
            return
        await self.mcp_app(scope, receive, send)

    async def _lifespan(self, receive: Receive, send: Send) -> None:
        message = await receive()
        if message["type"] != "lifespan.startup":
            return
        try:
            async with AsyncExitStack() as stack:
                await stack.enter_async_context(self.demo_app.router.lifespan_context(self.demo_app))
                await stack.enter_async_context(self.mcp_app.router.lifespan_context(self.mcp_app))
                await send({"type": "lifespan.startup.complete"})
                while True:
                    message = await receive()
                    if message["type"] == "lifespan.shutdown":
                        await send({"type": "lifespan.shutdown.complete"})
                        return
        except BaseException:
            await send({"type": "lifespan.startup.failed"})
            raise


def _is_demo_path(path: str) -> bool:
    return (
        path == "/"
        or path == "/example"
        or path == "/healthz"
        or path == "/favicon.ico"
        or path.startswith("/api/")
        or path.startswith("/static/")
    )


app = AzureDemoApp()
