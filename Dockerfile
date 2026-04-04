FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir httpx fastmcp

COPY mcp_server.py .

EXPOSE 8001

CMD ["python", "mcp_server.py", "--host", "0.0.0.0", "--port", "8001", "--transport", "streamable-http"]
