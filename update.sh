#!/bin/sh
# NovaTerrum Update-Script
# Ausführen: sudo sh /volume1/docker/NovaTerrum/update.sh

set -e
cd /volume1/docker/NovaTerrum

echo "→ Git pull..."
git pull origin main

echo "→ Docker Image neu bauen..."
docker build --no-cache -t novaterrum ./app

echo "→ Container neu starten..."
docker stop novaterrum 2>/dev/null || true
docker rm novaterrum 2>/dev/null || true
docker run -d \
  --name novaterrum \
  --restart unless-stopped \
  -p 8432:3000 \
  -e ANTHROPIC_API_KEY="$(grep ANTHROPIC_API_KEY /volume1/docker/NovaTerrum/.env | cut -d= -f2-)" \
  -v /volume1/docker/NovaTerrum/wiki:/wiki \
  novaterrum

echo "✓ Fertig — http://192.168.1.2:8432"
