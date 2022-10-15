# sasha-artsoul
It's web-site for nail business

start docker compose

from /deploy
docker-compose --compatibility -f docker-compose.yml up -d --force-recreate --build

with env

from project
docker-compose --env-file .env --compatibility -p artsoul -f ./deploy/docker-compose.local.yml up --build --remove-orphans -d
