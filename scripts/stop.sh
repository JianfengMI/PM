#!/usr/bin/env sh
set -eu

docker rm -f project-management-mvp >/dev/null 2>&1 || true
printf '%s\n' 'Project Management MVP stopped.'
