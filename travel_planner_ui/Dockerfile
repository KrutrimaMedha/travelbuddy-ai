# Stage 1: build
FROM node:20-alpine AS builder
WORKDIR /app

# copy dependency files first (better caching)
COPY travel_planner_ui/package*.json ./

# install dependencies
RUN npm ci

# copy rest of frontend source
COPY travel_planner_ui/ .

# copy env file created by workflow
COPY travel_planner_ui/.env.production .env.production

# build frontend
RUN npm run build

# Stage 2: serve static files
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html

# expose port 8080 for Cloud Run
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
