from __future__ import annotations

import argparse
from dataclasses import replace
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from minimalist_presentation_mcp.config import DEFAULT_BASE_URL, DEFAULT_HOST, DEFAULT_PORT, load_settings  # noqa: E402
from minimalist_presentation_mcp.mcp.server import create_mcp_server_from_settings  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Message-First Deck HTTP Streamable MCP server.")
    env_settings = load_settings()
    parser.add_argument("--host", default=env_settings.host or DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=env_settings.port or DEFAULT_PORT)
    parser.add_argument("--base-url", default=env_settings.public_base_url or DEFAULT_BASE_URL)
    args = parser.parse_args()

    settings = replace(
        load_settings(),
        host=args.host,
        port=args.port,
        public_base_url=args.base_url,
    )
    server = create_mcp_server_from_settings(settings)
    server.run(transport="streamable-http")


if __name__ == "__main__":
    main()
