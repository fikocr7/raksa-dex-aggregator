FROM python:3.12-slim

WORKDIR /app

# Install build deps for any wheels that need compilation
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
COPY app /app/app

RUN pip install --no-cache-dir -e .

# Railway / Render / Fly inject $PORT — default to 8000 for local
ENV PORT=8000
EXPOSE 8000

# Use shell form so $PORT is expanded at runtime
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
