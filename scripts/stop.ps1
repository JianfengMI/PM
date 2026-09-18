$ErrorActionPreference = "Stop"

$containerName = "project-management-mvp"
docker rm -f $containerName 2>$null
Write-Host "Project Management MVP stopped."
