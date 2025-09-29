#!/bin/sh

# chmod +x deploy.sh

docker compose down

git pull

docker compose up -d
