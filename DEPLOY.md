# Deploy to Your Own Server

## What You Need

- Server with Docker/Podman installed
- Domain (optional, for HTTPS)
- Git installed on server

## Quick Start

### 1. On Your Server

```bash
# Create directory
mkdir -p ~/kupkid.ru
cd ~/kupkid.ru

# Clone repository
git clone https://github.com/kupkid/kupkid.ru.git .
```

### 2. Build and Run

```bash
# Build container
podman build -t kupkid-site .

# Run with API server
podman run -d \
  --name kupkid-site \
  -p 8080:80 \
  -v $(pwd):/usr/share/caddy:Z \
  kupkid-site

# In another terminal, run API server
python3 server.py
```

### 3. Using Docker Compose (Easier)

Create `docker-compose.yml`:

```yaml
version: '3'
services:
  caddy:
    build: .
    ports:
      - "8080:80"
    volumes:
      - .:/usr/share/caddy:Z
    restart: unless-stopped
  
  api:
    image: python:3-alpine
    working_dir: /app
    volumes:
      - .:/app:Z
    command: python3 server.py
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

### 4. Making Changes

```bash
# Edit files locally or on server
vim notes/new-post.html

# Rebuild notes.json
python3 server.py &
curl http://localhost:8081/api/rebuild

# Or it auto-rebuilds every 5 seconds when files change

# Commit changes
git add .
git commit -m "add new post"
git push origin main
```

## File Structure

```
kupkid.ru/
├── index.html          # Main page
├── about.html          # About page
├── notes/              # Your posts
│   ├── winter.html
│   ├── bot.html
│   └── ...
├── notes.json          # Auto-generated index
├── server.py           # API server (commits + rebuild)
├── Caddyfile           # Web server config
├── Dockerfile          # Container definition
└── docker-compose.yml  # Easy deployment
```

## Adding New Note

1. Create file in `notes/my-post.html`:
```html
<!--
date: 2025-02-20
title: my new post
title_ru: мой новый пост
tags: learning, code
-->
```

2. File auto-detected and added to notes.json
3. Appears on site immediately

## Git Workflow

```bash
# On server, after editing
git add .
git commit -m "update: new note about X"
git push

# Changelog shows commit automatically
```

## HTTPS (with domain)

Uncomment in `Caddyfile`:
```
:443 {
    root * /usr/share/caddy
    file_server
    tls your@email.com
}
```

Caddy auto-gets Let's Encrypt certificate.

## Troubleshooting

**Site not updating?**
```bash
# Force rebuild
curl http://localhost:8081/api/rebuild
```

**Permissions?**
```bash
# Fix SELinux
chcon -R -t container_file_t .
```

**Port already in use?**
```bash
# Change port in docker-compose.yml
ports:
  - "8081:80"  # Instead of 8080:80
```
