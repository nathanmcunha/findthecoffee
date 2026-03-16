# Stage 1: Build the CSS
FROM alpine:latest AS builder

# Set the Tailwind version
ENV TAILWIND_VERSION=v4.2.1

# Download the Standalone CLI binary (linux-x64)
RUN apk add --no-cache wget ca-certificates \
    && wget -q https://github.com/tailwindlabs/tailwindcss/releases/download/${TAILWIND_VERSION}/tailwindcss-linux-x64 -O /usr/local/bin/tailwindcss \
    && chmod +x /usr/local/bin/tailwindcss

WORKDIR /app
COPY . .

# Compile the CSS (it will scan index.html and script.js based on tailwind.config.js)
RUN /usr/local/bin/tailwindcss -i input.css -o style.css --minify

# Stage 2: Serve the application
FROM nginx:alpine
COPY --from=builder /app/index.html /usr/share/nginx/html/
COPY --from=builder /app/script.js /usr/share/nginx/html/
COPY --from=builder /app/style.css /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
