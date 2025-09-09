#!/bin/bash

# Скрипт для деплоя приложения на сервер

set -e

SSH_KEY_PATH="~/.ssh/id_ed25519"
SERVER="ubuntu@54.88.62.150"
SERVER_DIR="rag_app"

echo "🚀 Начинаю деплой на сервер..."

# Создаем директорию на сервере если её нет
echo "📁 Создаю директорию на сервере..."
ssh -i "$SSH_KEY_PATH" "$SERVER" "mkdir -p $SERVER_DIR"

# Копируем необходимые файлы на сервер
echo "📤 Копирую файлы на сервер..."
scp -i "$SSH_KEY_PATH" ./docker-compose.prod.yml "$SERVER":~/"$SERVER_DIR"/docker-compose.yml

# Копируем конфигурационные файлы
scp -i "$SSH_KEY_PATH" ./server/src/config.yml "$SERVER":~/"$SERVER_DIR"/
scp -i "$SSH_KEY_PATH" ./server/src/prompts.yml "$SERVER":~/"$SERVER_DIR"/
scp -i "$SSH_KEY_PATH" -r ./server/src/scenarios "$SERVER":~/"$SERVER_DIR"/

# Создаем только пустую директорию data (файлы chunks и book_sample.pdf не нужны)
echo "📁 Создаю директорию data на сервере..."
ssh -i "$SSH_KEY_PATH" "$SERVER" "mkdir -p $SERVER_DIR/data"

# Деплоим на сервере
echo "🎯 Запускаю приложение на сервере..."
ssh -i "$SSH_KEY_PATH" "$SERVER" << 'EOF'
    cd rag_app
    
    # Останавливаем старые контейнеры
    docker-compose down || true
    
    # Удаляем старые образы
    docker image prune -f || true
    
    # Скачиваем последние образы
    docker-compose pull
    
    # Запускаем приложение
    docker-compose up -d
    
    echo "✅ Приложение успешно запущено!"
    echo "🌐 Фронтенд доступен по адресу: http://54.88.62.150:7001"
    echo "🔧 API доступен по адресу: http://54.88.62.150:7000"
    
    # Показываем статус контейнеров
    echo ""
    echo "📊 Статус контейнеров:"
    docker-compose ps
EOF

echo "🎉 Деплой завершен!"