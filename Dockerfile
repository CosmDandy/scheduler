# FROM python:3.11-slim
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

LABEL authors="cosmdandy"

WORKDIR /app
COPY . .
RUN uv init && uv add nylas pytz

ENV HOME=1
ENV MORNING=1
ENV REPEAT=1
ENV TZ="Europe/Moscow"

CMD ["uv", "run", "main.py"]
