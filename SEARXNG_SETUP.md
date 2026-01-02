# SearXNG Setup Guide

This guide explains how to set up SearXNG for use with the Python version of Perplexica.

## Quick Start (Docker)

### 1. Update SearXNG Configuration

Edit `searxng/settings.yml` and ensure the following:

```yaml
use_default_settings: true

general:
  instance_name: 'perplexica'

search:
  autocomplete: 'google'
  formats:
    - html
    - json

server:
  secret_key: 'your-secret-key-here'
  limiter: false  # IMPORTANT: Disable rate limiter for API access
```

**Key Setting**: `server: limiter: false` is required to enable JSON API access.

### 2. Start SearXNG Container

```bash
docker run -d \
  --name searxng \
  -p 4000:8080 \
  -v "$(pwd)/searxng/settings.yml:/etc/searxng/settings.yml:ro" \
  -e "SEARXNG_SECRET=$(openssl rand -hex 32)" \
  searxng/searxng:latest
```

### 3. Verify It's Working

```bash
# Test the JSON API
curl -s 'http://localhost:4000/search?q=test&format=json' | python3 -m json.tool | head -20
```

You should see JSON search results.

### 4. Update Perplexica Config

Edit `config.json`:

```json
{
  "search": {
    "searxng_url": "http://localhost:4000",
    "timeout": 30,
    "max_results": 10
  }
}
```

### 5. Test Perplexica

```bash
python perplexica.py "What is Python?"
```

## Troubleshooting

### 403 Forbidden Error

**Problem**: API returns 403 Forbidden

**Solution**: Make sure `limiter: false` is set in `searxng/settings.yml` and the container has been recreated with the mounted configuration:

```bash
docker stop searxng
docker rm searxng
# Run the docker run command again
```

### Container Logs Show "missing limiter.toml"

This is expected when `limiter: false` is set. It's not an error.

### No Search Results

1. Check SearXNG is running: `docker ps | grep searxng`
2. Check logs: `docker logs searxng`
3. Test API directly: `curl 'http://localhost:4000/search?q=test&format=json'`
4. Verify Perplexica config points to correct URL

### Connection Timeout

1. Verify SearXNG is accessible: `curl http://localhost:4000`
2. Check if port 4000 is already in use
3. Try setting `"verify_ssl": false` in config.json

## Advanced Configuration

### Enable Multiple Engines

Edit `searxng/settings.yml`:

```yaml
engines:
  - name: google
    disabled: false
  - name: bing
    disabled: false
  - name: duckduckgo
    disabled: false
```

### Custom Rate Limiting

If you want to enable rate limiting with exceptions for localhost:

```yaml
server:
  limiter: true

# Create searxng/limiter.toml:
[botdetection.ip_limit]
filter_link_local = false  # Don't limit localhost
```

### Using Public SearXNG Instances

**Warning**: Most public instances block automated API requests.

If you find one that works, update `config.json`:

```json
{
  "search": {
    "searxng_url": "https://your-searxng-instance.com"
  }
}
```

## Production Deployment

For production use:

1. **Enable rate limiting**: Set `limiter: true` in settings.yml
2. **Use a reverse proxy**: nginx or traefik
3. **Set up authentication**: Add basic auth or OAuth
4. **Configure CORS**: Restrict to your domain
5. **Use HTTPS**: Enable SSL/TLS
6. **Monitor resources**: Set up logging and metrics

## Docker Compose Example

```yaml
version: '3.8'

services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    ports:
      - "4000:8080"
    volumes:
      - ./searxng/settings.yml:/etc/searxng/settings.yml:ro
    environment:
      - SEARXNG_SECRET=${SEARXNG_SECRET}
    restart: unless-stopped
```

Run with:

```bash
export SEARXNG_SECRET=$(openssl rand -hex 32)
docker-compose up -d
```

## References

- [SearXNG Official Documentation](https://docs.searxng.org)
- [SearXNG Settings Documentation](https://docs.searxng.org/admin/settings/settings.html)
- [SearXNG Limiter Documentation](https://docs.searxng.org/admin/searx.limiter.html)
