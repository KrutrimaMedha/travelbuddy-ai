# ---- Stage 1: Build ----
FROM node:20-alpine AS builder
WORKDIR /app

# Better layer caching
COPY package*.json ./
RUN npm ci

# Copy the rest of the app (context is travel_planner_ui/)
# This includes the .env.production your workflow wrote
COPY . .

# Build
RUN npm run build

# ---- Stage 2: Serve ----
FROM nginx:alpine

# Serve the built app
COPY --from=builder /app/dist /usr/share/nginx/html

# Cloud Run expects the app to listen on $PORT (we'll use 8080)
# Replace default server to listen on 8080 and support SPA routing
COPY <<'EOF' /etc/nginx/conf.d/default.conf
server {
  listen 8080;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri /index.html;
  }
}
EOF

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
