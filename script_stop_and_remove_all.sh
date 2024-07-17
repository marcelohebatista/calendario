#!/bin/bash

docker stop $(docker ps -aq)
docker rm $(docker ps -aq)

docker rmi $(docker images -q)
docker rmi -f $(docker images -q)

docker volume rm $(docker volume ls -q)

docker network prune

docker system prune -a --volumes

echo "All Contêineres removidos."
