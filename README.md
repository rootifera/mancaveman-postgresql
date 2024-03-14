# mancaveman

docker compose build:

docker compose up -d postgres redis
DOCKER_BUILDKIT=0 docker compose build

because buildx is shit

and docker compose clean up:

docker compose down --rmi all --volumes

add the new scripts here