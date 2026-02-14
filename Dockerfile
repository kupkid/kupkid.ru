FROM docker.io/caddy:2-alpine

# Install Python for notes generation
RUN apk add --no-cache python3 py3-pip git

# Copy website files
COPY . /usr/share/caddy/

# Copy Caddyfile
COPY Caddyfile /etc/caddy/Caddyfile

# Make server.py executable
RUN chmod +x /usr/share/caddy/server.py

# Expose ports
EXPOSE 80 443

# Start Caddy
CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile"]
