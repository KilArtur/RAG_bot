#!/bin/bash

# Скрипт для сборки и загрузки образов в Docker Hub для продакшна

set -e

echo "🚀 Начинаю сборку и загрузку образов для продакшна..."

# Проверяем что пользователь авторизован в Docker Hub
if ! docker info | grep -q "kildiyarovartur"; then
    echo "⚠️  Необходимо авторизоваться в Docker Hub:"
    echo "docker login"
    exit 1
fi

# Собираем образ бэкенда
echo "📦 Собираю образ бэкенда..."
docker build -f server/Dockerfile.prod -t kildiyarovartur/rag_api:latest ./server/

# Собираем образ фронтенда  
echo "📦 Собираю образ фронтенда..."
docker build -f front/Dockerfile.prod -t kildiyarovartur/rag_frontend:latest ./front/

# Загружаем образы в Docker Hub
echo "⬆️  Загружаю образ бэкенда в Docker Hub..."
docker push kildiyarovartur/rag_api:latest

echo "⬆️  Загружаю образ фронтенда в Docker Hub..."
docker push kildiyarovartur/rag_frontend:latest

echo "✅ Образы успешно собраны и загружены в Docker Hub!"