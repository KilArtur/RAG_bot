FROM nginx:alpine

# Копирование конфигурации Nginx
COPY ../nginx.conf /etc/nginx/nginx.conf

# Копирование статических файлов
COPY . /usr/share/nginx/html/

# Установка прав доступа
RUN chmod -R 755 /usr/share/nginx/html

# Открытие порта
EXPOSE 80

# Запуск Nginx
CMD ["nginx", "-g", "daemon off;"]