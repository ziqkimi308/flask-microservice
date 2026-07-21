#!/bin/bash

set -euo pipefail

# Take 1st argument and also default to empty string if not provided
# Take 2nd argument and also default to 'latest' if not provided

DOCKER_IMAGE="${1:-}"
APP_VERSION="${2:-latest}"
DEPLOY_DIR="/home/ubuntu/flask-microservice"
ENV_FILE="$DEPLOY_DIR/.env"
COMPOSE_FILE="$DEPLOY_DIR/docker-compose.prod.yml"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

if [[ -z "$DOCKER_IMAGE" ]]; then
    log "ERROR: DOCKER_IMAGE argument is required"
    log "Usage: bash deploy.sh <image:tag> <version>"
    exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
    log "ERROR: .env file not found at $ENV_FILE"
    exit 1
fi

log "Starting deployment of $DOCKER_IMAGE (version: $APP_VERSION)"

export DOCKER_IMAGE="$DOCKER_IMAGE"
export APP_VERSION="$APP_VERSION"

source "$ENV_FILE"

log "Pulling latest image..."
docker pull "$DOCKER_IMAGE"

log "Stopping existing containers..."
docker compose -f "$COMPOSE_FILE" down --remove-orphans || true

log "Starting new containers..."
docker compose -f "$COMPOSE_FILE" up -d

log "Waiting for health check..."
sleep 15

# silent 
HEALTH_STATUS=$(curl -sf http://localhost:5000/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null || echo "unreachable")

if [[ "$HEALTH_STATUS" != "ok" ]]; then
    log "ERROR: Health check failed — status: $HEALTH_STATUS"
    log "Rolling back to previous containers..."
    docker compose -f "$COMPOSE_FILE" down
    exit 1
fi

log "Health check passed — deployment successful"
log "Service running at http://$(curl -sf http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'localhost'):5000"

# prune = remove all unused docker images
docker image prune -f
log "Cleaned up unused images"