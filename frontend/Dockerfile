# Stage 1: Type check + Build
FROM alpine:latest AS builder

ENV TAILWIND_VERSION=v4.2.1
ENV ESBUILD_VERSION=0.25.2
ENV DENO_VERSION=2.3.1

RUN apk add --no-cache wget ca-certificates curl tar

# Download standalone binaries
RUN wget -q https://github.com/tailwindlabs/tailwindcss/releases/download/${TAILWIND_VERSION}/tailwindcss-linux-x64 -O /usr/local/bin/tailwindcss \
    && chmod +x /usr/local/bin/tailwindcss

RUN wget -q https://github.com/denoland/deno/releases/download/v${DENO_VERSION}/deno-x86_64-unknown-linux-gnu.zip -O /tmp/deno.zip \
    && unzip /tmp/deno.zip -d /usr/local/bin \
    && chmod +x /usr/local/bin/deno \
    && rm /tmp/deno.zip

RUN wget -qO- https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-${ESBUILD_VERSION}.tgz \
    | tar xz --strip-components=2 -C /usr/local/bin package/bin/esbuild \
    && chmod +x /usr/local/bin/esbuild

WORKDIR /app
COPY . .

# Type check → Bundle JS → Compile CSS
RUN deno check src/main.ts
RUN esbuild src/main.ts --bundle --outfile=script.js --minify
RUN tailwindcss -i input.css -o style.css --minify

# Stage 2: Serve the application
FROM nginx:alpine
COPY --from=builder /app/index.html /usr/share/nginx/html/
COPY --from=builder /app/script.js /usr/share/nginx/html/
COPY --from=builder /app/style.css /usr/share/nginx/html/

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
