from __future__ import annotations

import json
from typing import Any

from example.communication_compiler.config import AppSettings
from minimalist_presentation_mcp.deck.service import create_deck_response
from minimalist_presentation_mcp.storage.deck_store import DeckStore


class McpDeckClient:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    async def create_message_first_deck(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            return await self._call_remote_mcp(payload)
        except Exception as exc:
            if not self.settings.allow_local_mcp_fallback:
                raise
            response = create_deck_response(
                format=str(payload["format"]),
                content=payload["content"],
                store=DeckStore(self.settings.message_first_mcp_data_dir),
                base_url=self.settings.message_first_public_base_url,
            )
            warnings = list(response.get("warnings", []))
            warnings.append(f"MCP_REMOTE_UNAVAILABLE_USED_LOCAL_FALLBACK: {type(exc).__name__}")
            response["warnings"] = warnings
            return response

    async def _call_remote_mcp(self, payload: dict[str, Any]) -> dict[str, Any]:
        import httpx
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        headers = {}
        if self.settings.message_first_mcp_bearer_token:
            headers["Authorization"] = f"Bearer {self.settings.message_first_mcp_bearer_token}"
        if headers:
            async with httpx.AsyncClient(headers=headers) as http_client:
                result = await self._call_tool(payload, http_client=http_client)
        else:
            result = await self._call_tool(payload, http_client=None)
        if result.isError:
            raise RuntimeError(_tool_result_text(result) or "MCP tool returned an error")
        if result.structuredContent:
            return dict(result.structuredContent)
        text = _tool_result_text(result)
        if text:
            return json.loads(text)
        raise RuntimeError("MCP tool returned no structured content")

    async def _call_tool(self, payload: dict[str, Any], *, http_client: Any) -> Any:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with streamable_http_client(self.settings.message_first_mcp_endpoint, http_client=http_client) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return await session.call_tool(
                    "create_message_first_deck",
                    {"format": payload["format"], "content": payload["content"]},
                )


def _tool_result_text(result: Any) -> str:
    parts: list[str] = []
    for item in getattr(result, "content", []) or []:
        text = getattr(item, "text", None)
        if text:
            parts.append(str(text))
    return "\n".join(parts)
