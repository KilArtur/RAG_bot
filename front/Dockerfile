FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf

COPY . /usr/share/nginx/html/

RUN chmod -R 755 /usr/share/nginx/html && \
    chown -R nginx:nginx /usr/share/nginx/html

EXPOSE 7001

CMD ["nginx", "-g", "daemon off;"]