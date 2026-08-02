# RAG FastAPI - Deployment Guide

## Deployment Options

---

## 1. Docker Deployment

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run server
CMD ["uv", "run", "fastapi", "dev", "app/main.py", "--host", "0.0.0.0"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_CHAT_MODEL: gpt-4-turbo
      OPENAI_EMBEDDING_MODEL: text-embedding-3-small
      CHROMA_PATH: /data/chroma
      COLLECTION_NAME: rag_docs
    volumes:
      - chroma_data:/data/chroma
    restart: unless-stopped

volumes:
  chroma_data:
    driver: local
```

### Build and Run

```bash
# Build image
docker build -t rag-fastapi .

# Run with environment file
docker run -p 8000:8000 --env-file .env rag-fastapi

# Or with docker-compose
docker-compose up -d
```

---

## 2. Gunicorn + Uvicorn (Production)

### Install Gunicorn

```bash
uv pip install gunicorn
```

### Create gunicorn_config.py

```python
import multiprocessing

# Server settings
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 300
keepalive = 5

# Logging
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"

# Process naming
proc_name = "rag-fastapi"
```

### Run with Gunicorn

```bash
gunicorn app.main:app -c gunicorn_config.py
```

---

## 3. Systemd Service (Linux VPS)

### Create /etc/systemd/system/rag-fastapi.service

```ini
[Unit]
Description=RAG FastAPI Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/www/rag-fastapi
EnvironmentFile=/home/www/rag-fastapi/.env
ExecStart=/home/www/rag-fastapi/.venv/bin/gunicorn app.main:app -c gunicorn_config.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

### Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable rag-fastapi
sudo systemctl start rag-fastapi
sudo systemctl status rag-fastapi
```

---

## 4. AWS Lambda

### Install Serverless Framework

```bash
npm install -g serverless
```

### serverless.yml

```yaml
service: rag-fastapi

provider:
  name: aws
  runtime: python3.12
  region: us-east-1
  environment:
    OPENAI_API_KEY: ${env:OPENAI_API_KEY}
    CHROMA_PATH: /tmp/chroma
    COLLECTION_NAME: rag_docs

functions:
  api:
    handler: app.main.app
    events:
      - http:
          path: /{proxy+}
          method: ANY
      - http:
          path: /
          method: ANY

plugins:
  - serverless-python-requirements
```

### Deploy

```bash
serverless deploy
```

---

## 5. Google Cloud Run

### Create .dockerignore

```
.git
.gitignore
.env
.venv
__pycache__
*.pyc
.pytest_cache
chroma/
```

### Deploy

```bash
# Build and push to Cloud Build
gcloud builds submit --tag gcr.io/PROJECT_ID/rag-fastapi

# Deploy to Cloud Run
gcloud run deploy rag-fastapi \
  --image gcr.io/PROJECT_ID/rag-fastapi \
  --platform managed \
  --region us-central1 \
  --memory 1Gi \
  --set-env-vars OPENAI_API_KEY=sk-proj-xxx
```

---

## 6. Heroku

### Procfile

```
web: gunicorn app.main:app -w 4 -b 0.0.0.0:$PORT
```

### requirements.txt

```bash
uv pip freeze > requirements.txt
```

### Deploy

```bash
heroku login
heroku create rag-fastapi
heroku config:set OPENAI_API_KEY=sk-proj-xxx
git push heroku main
```

---

## 7. Nginx Reverse Proxy

### /etc/nginx/sites-available/rag-fastapi

```nginx
upstream rag_fastapi {
    server localhost:8000;
}

server {
    listen 80;
    server_name rag-api.example.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name rag-api.example.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/rag-api.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/rag-api.example.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy settings
    location / {
        proxy_pass http://rag_fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}
```

### Enable

```bash
sudo ln -s /etc/nginx/sites-available/rag-fastapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Production Configuration

### Environment Variables

```bash
# .env.production
OPENAI_API_KEY=sk-proj-xxx-production
OPENAI_CHAT_MODEL=gpt-4-turbo              # Better quality
OPENAI_EMBEDDING_MODEL=text-embedding-3-large  # Better accuracy
CHROMA_PATH=/data/chroma                   # Persistent volume
COLLECTION_NAME=rag_docs_prod
```

### Database Persistence

**Important:** ChromaDB data must be persistent!

```bash
# Create persistent volume
mkdir -p /data/chroma
chmod 755 /data/chroma

# For Docker, mount volume
docker run -v /data/chroma:/data/chroma rag-fastapi
```

### Monitoring

#### Logging

```python
# In app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    logger.info(f"Ingesting file: {file.filename}")
    # ...
```

#### Health Checks

```bash
# Kubernetes liveness probe
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

# Readiness probe
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Performance Optimization

1. **Increase Workers**
   ```
   workers = cpu_count * 2 + 1
   ```

2. **Connection Pooling**
   ```python
   # In llm.py
   from openai import OpenAI, AsyncOpenAI
   client = AsyncOpenAI()  # For async
   ```

3. **Caching** (Future enhancement)
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=100)
   def embed_texts(texts):
       # Cache embeddings
   ```

4. **Database Indexing**
   ChromaDB automatically indexes vectors using HNSW

### Backup & Recovery

```bash
# Backup ChromaDB
tar -czf chroma_backup_$(date +%Y%m%d).tar.gz /data/chroma/

# Restore ChromaDB
tar -xzf chroma_backup_20240101.tar.gz -C /data/
```

---

## Security Best Practices

### 1. API Key Management
- [ ] Never commit `.env` to version control
- [ ] Use secrets manager (AWS Secrets Manager, HashiCorp Vault)
- [ ] Rotate keys regularly
- [ ] Use restricted API keys with specific permissions

### 2. Network Security
- [ ] Use HTTPS/TLS for all communications
- [ ] Implement rate limiting
- [ ] Use WAF (Web Application Firewall)
- [ ] Enable CORS only for trusted origins

### 3. Data Protection
- [ ] Encrypt data at rest
- [ ] Encrypt data in transit (TLS)
- [ ] Regular backups
- [ ] Database access controls

### 4. Application Security
- [ ] Run as non-root user
- [ ] Use read-only filesystems where possible
- [ ] Implement authentication/authorization
- [ ] Regular security updates

### Example: Docker with Security

```dockerfile
FROM python:3.12-slim

# Non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app
RUN chown -R appuser:appuser /app

USER appuser

COPY --chown=appuser:appuser . .
RUN uv sync --frozen

EXPOSE 8000
CMD ["uv", "run", "fastapi", "dev", "app/main.py", "--host", "0.0.0.0"]
```

---

## Scaling Considerations

### Horizontal Scaling
- Multiple instances behind load balancer
- Shared ChromaDB instance (or replicated)
- Stateless design (current implementation)

### Vertical Scaling
- Increase instance size
- Use larger embedding model (text-embedding-3-large)
- Increase worker count

### Database Scaling
- ChromaDB: Use managed service (if available)
- For large deployments (>1M documents):
  - Consider Weaviate, Pinecone, or Milvus
  - Implement sharding by document type/source

---

## Monitoring & Alerting

### Key Metrics
- Request latency (p50, p95, p99)
- Error rate
- API token usage & cost
- Disk space (ChromaDB)
- CPU/Memory usage

### Example: CloudWatch (AWS)
```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def put_metric(name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='RAGFastAPI',
        MetricData=[{
            'MetricName': name,
            'Value': value,
            'Unit': unit,
        }]
    )
```

---

## Troubleshooting Deployment

### Issue: 502 Bad Gateway
- Check if app is running: `curl http://localhost:8000/health`
- Check logs: `journalctl -u rag-fastapi -f`
- Verify API key is set

### Issue: Out of Memory
- Check ChromaDB size: `du -sh /data/chroma`
- Increase container memory limits
- Implement document cleanup/archival

### Issue: Slow Queries
- Monitor latency: `curl -w '@curl-format.txt' http://localhost:8000/ask`
- Check OpenAI API status
- Profile with `scalene` or `py-spy`

---

## Rollback Plan

```bash
# Keep previous image
docker tag rag-fastapi:latest rag-fastapi:v1.0.0

# Quick rollback
docker run -d rag-fastapi:v1.0.0

# Or with systemd
systemctl stop rag-fastapi
git checkout previous-commit
systemctl start rag-fastapi
```

---

## Checklist

- [ ] Dockerfile created and tested locally
- [ ] Environment variables configured securely
- [ ] Database persistence configured
- [ ] Logging enabled
- [ ] Health checks implemented
- [ ] HTTPS/TLS configured
- [ ] Rate limiting enabled
- [ ] Monitoring and alerting set up
- [ ] Backup and recovery plan documented
- [ ] Security review completed
- [ ] Load testing completed
- [ ] Documentation updated
