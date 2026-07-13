# CWS Internal Development Coordinator - backend image.
# Migrations run at container start (alembic upgrade head) so the app and
# schema can never drift apart in a deployment.

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY app ./app

EXPOSE 8000

# Config comes from IDC_-prefixed environment variables (see .env.example);
# there is deliberately no .env baked into the image.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
