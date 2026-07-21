# Stage 1 - Builder
FROM python:3.11-alpine AS builder

# There is no left-over downloaded packages because of --no-cache
RUN apk add --no-cache \
	gcc \
	musl-dev \
	libffi-dev \
	postgresql-dev

WORKDIR /builder

COPY requirements.txt .

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2 - Final
FROM python:3.11-alpine AS Final

RUN apk add --no-cache \
	libpq \
	dumb-init

COPY --from=builder /install /usr/local

WORKDIR /app

# 'app/' here is host's app folder, not the newly created workdir
COPY app/ ./app/

RUN addgroup -S appgroup && \
	adduser -S appuser -G appgroup -u 1001

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

ENV FLASK_APP=app \
    FLASK_ENV=production \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENTRYPOINT ["dumb-init", "--"]
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]