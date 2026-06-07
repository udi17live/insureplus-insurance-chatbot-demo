#!/bin/bash
set -e

ACR="insureplusacr.azurecr.io"
TAG=${1:-latest}

echo "==> Logging in to ACR..."
az acr login --name insureplusacr

echo "==> Building backend..."
docker build -t $ACR/backend:$TAG ./backend
echo "==> Pushing backend..."
docker push $ACR/backend:$TAG

echo "==> Building frontend..."
docker build -t $ACR/frontend:$TAG ./frontend
echo "==> Pushing frontend..."
docker push $ACR/frontend:$TAG

echo ""
echo "Done! Images pushed:"
echo "  $ACR/backend:$TAG"
echo "  $ACR/frontend:$TAG"
