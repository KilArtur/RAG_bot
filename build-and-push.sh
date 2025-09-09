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
echo ""
echo "Следующие шаги:"
echo "1. Скопируйте файлы на сервер:"
echo "   scp -i SSH/KEY/PATH -r ./server/src/config.yml ./server/src/prompts.yml ./server/src/scenarios ./data ./docker-compose.prod.yml ubuntu@54.88.62.150:~/rag_app/"
echo ""
echo "2. Подключитесь к серверу и запустите приложение:"
echo "   ssh -i SSH/KEY/PATH ubuntu@54.88.62.150"
echo "   cd rag_app && docker-compose -f docker-compose.prod.yml up -d"