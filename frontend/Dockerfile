# Stage 1: Build frontend with Vite
FROM node:20-alpine AS builder

ARG API_BASE_URL="http://localhost:5000/api/v1"
ENV API_BASE_URL=${API_BASE_URL}

WORKDIR /app
COPY . .

# Install dependencies and build
RUN cd frontend && npm install && npm run build

# Stage 2: Serve the static bundle from Nginx
FROM nginx:alpine
COPY --from=builder /app/frontend/dist/ /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
