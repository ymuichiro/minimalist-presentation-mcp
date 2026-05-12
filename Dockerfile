FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV MESSAGE_FIRST_DECK_HOST=0.0.0.0
ENV MESSAGE_FIRST_DECK_PORT=3000
ENV MESSAGE_FIRST_DECK_DATA_DIR=/data

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir .

RUN mkdir -p /data \
  && chown -R nobody:nogroup /data

USER nobody
EXPOSE 3000
CMD ["minimalist-presentation-mcp"]
