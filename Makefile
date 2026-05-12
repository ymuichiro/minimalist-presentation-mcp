HOST ?= 127.0.0.1
PORT ?= 3000
COMPOSE := docker compose

.PHONY: help sync run test init-env up up-tunnel down restart ps logs logs-app logs-tunnel clean

help:
	@echo "Available targets:"
	@echo "  make sync          Install dependencies with uv"
	@echo "  make run           Start the server directly on $(HOST):$(PORT)"
	@echo "  make test          Run test suite"
	@echo "  make init-env      Create .env from .env.example if missing"
	@echo "  make up            Start local container stack on 127.0.0.1:\$${APP_PORT:-13000}"
	@echo "  make up-tunnel     Start container stack plus named Cloudflare Tunnel"
	@echo "  make down          Stop and remove compose stack"
	@echo "  make restart       Restart local container stack"
	@echo "  make ps            Show compose service status"
	@echo "  make logs          Follow all compose logs"
	@echo "  make logs-app      Follow app logs"
	@echo "  make logs-tunnel   Follow cloudflared logs"
	@echo "  make clean         Remove local runtime/test artifacts"

sync:
	uv sync

run:
	MESSAGE_FIRST_DECK_HOST=$(HOST) MESSAGE_FIRST_DECK_PORT=$(PORT) uv run minimalist-presentation-mcp

test:
	uv run pytest

init-env:
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example"; else echo ".env already exists"; fi

up:
	$(COMPOSE) up -d --build

up-tunnel:
	$(COMPOSE) --profile tunnel up -d --build

down:
	$(COMPOSE) down

restart: down up

ps:
	$(COMPOSE) ps

logs:
	$(COMPOSE) logs -f

logs-app:
	$(COMPOSE) logs -f app

logs-tunnel:
	$(COMPOSE) logs -f cloudflared

clean:
	rm -rf .pytest_cache data
