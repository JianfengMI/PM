@echo off
setlocal
set IMAGE_NAME=project-management-mvp
set CONTAINER_NAME=project-management-mvp

docker build -t %IMAGE_NAME% .
docker rm -f %CONTAINER_NAME% >nul 2>&1
if exist .env (
	docker run -d --name %CONTAINER_NAME% -p 3000:8000 --env-file .env %IMAGE_NAME%
) else (
	docker run -d --name %CONTAINER_NAME% -p 3000:8000 %IMAGE_NAME%
)
echo Project Management MVP is running at http://127.0.0.1:3000
