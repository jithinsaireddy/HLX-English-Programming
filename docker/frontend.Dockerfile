FROM node:18-alpine AS build
WORKDIR /app
COPY ui/english-ui/ /app/
RUN npm ci || npm i && npm run build

FROM nginx:alpine
COPY --from=build /app/dist/ /usr/share/nginx/html/
# Nginx config: serve SPA and proxy /api to backend web container
RUN printf 'server {\n  listen 80;\n  location / {\n    root /usr/share/nginx/html;\n    try_files $uri /index.html;\n  }\n  location /api/ {\n    proxy_pass http://web:5000/;\n    proxy_set_header Host $host;\n    proxy_set_header X-Real-IP $remote_addr;\n    add_header Access-Control-Allow-Origin * always;\n    add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;\n    add_header Access-Control-Allow-Headers "Content-Type" always;\n    if ($request_method = OPTIONS) {\n      return 204;\n    }\n  }\n}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 80

