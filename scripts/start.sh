#!/usr/bin/env sh
set -eu

IMAGE_NAME="project-management-mvp"
CONTAINER_NAME="project-management-mvp"

docker build -t "$IMAGE_NAME" .
docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
if [ -f .env ]; then
	docker run -d --name "$CONTAINER_NAME" -p 3000:8000 --env-file .env "$IMAGE_NAME"
else
	docker run -d --name "$CONTAINER_NAME" -p 3000:8000 "$IMAGE_NAME"
fi
printf '%s\n' 'Project Management MVP is running at http://127.0.0.1:3000'
