FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

FROM base AS development
EXPOSE 5000
CMD ["sh", "-c", "python -m flask --app run.py db upgrade && exec python -m flask --app run.py run --host=0.0.0.0 --port=5000 --debug"]

FROM base AS production
EXPOSE 5000
CMD ["sh", "-c", "python -m flask --app run.py db upgrade && exec waitress-serve --host=0.0.0.0 --port=5000 --call app:create_app"]
