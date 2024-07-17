#!/bin/bash

# Para os contêineres Docker
docker-compose down

# Remove os diretórios __pycache__
find . -type d -name "__pycache__" -exec rm -r {} +

echo "Contêineres parados e diretórios __pycache__ removidos."
