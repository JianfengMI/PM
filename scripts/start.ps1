$ErrorActionPreference = "Stop"

$imageName = "project-management-mvp"
$containerName = "project-management-mvp"
$envFile = if (Test-Path ".env") { @("--env-file", ".env") } else { @() }

docker build -t $imageName .
docker rm -f $containerName 2>$null
docker run -d --name $containerName -p 3000:8000 @envFile $imageName
Write-Host "Project Management MVP is running at http://127.0.0.1:3000"
