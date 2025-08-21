FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir -e .

EXPOSE 8080

CMD ["python", "-m", "kong_mcp_server.server"]