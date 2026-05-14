# Metamorph Deployment Guide

This guide provides comprehensive instructions for deploying the Metamorph system to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling and Performance](#scaling-and-performance)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## Prerequisites

### System Requirements

- **Docker**: Version 20.10+ with Docker Compose v2
- **Hardware**: Minimum 4 CPU cores, 8GB RAM, 50GB disk space
- **Operating System**: Linux (Ubuntu 20.04/22.04 recommended)
- **Domain**: Configured domain name with SSL certificates
- **Network**: Ports 80, 443, 8000, 3000, 5432, 6379, 9000-9001 open

### Required Services

- **PostgreSQL**: Version 13+ with pgvector extension
- **Redis**: Version 6+ for caching and task queue
- **MinIO/S3**: Object storage for file uploads
- **Wiki.js**: For documentation (optional but recommended)
- **LiteLLM Proxy**: For LLM integration (optional)

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/metamorph.git
cd metamorph
```

### 2. Create Environment Files

Copy the example environment files and configure them:

```bash
cp .env.example .env
cp .env.production .env  # For production
cp .env.staging .env     # For staging
```

### 3. Generate Secrets

Generate strong secrets for production:

```bash
# Generate secret key (32+ characters)
openssl rand -hex 32

# Generate API keys
openssl rand -hex 16
```

## Configuration

### Environment Variables

Edit `.env` file with your specific configuration:

```env
# Database
POSTGRES_DB=metamorph_prod
POSTGRES_USER=metamorph_user
POSTGRES_PASSWORD=your_strong_password
DATABASE_URL=postgresql+psycopg2://metamorph_user:your_strong_password@postgres:5432/metamorph_prod

# Vector Search (pgvector)
VECTOR_DB_URL=postgresql+psycopg2://metamorph_user:your_strong_password@postgres:5432/metamorph_prod
VECTOR_DIMENSIONS=384  # For sentence-transformers all-MiniLM-L6-v2
VECTOR_INDEX_TYPE=HNSW  # or IVFFlat for different performance characteristics
VECTOR_M=16  # HNSW parameter
VECTOR_EF_CONSTRUCTION=64  # HNSW parameter
VECTOR_EF_SEARCH=40  # HNSW parameter
```

### PostgreSQL pgvector Setup

To enable pgvector extension:

```sql
-- Connect to your database
psql -h localhost -U metamorph_user -d metamorph_prod

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Create vector table example
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(255) NOT NULL,
    embedding vector(384) NOT NULL,  -- Dimension matches your embedding model
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_document_embeddings_hnsw 
ON document_embeddings USING hnsw (embedding vector_hnsw_ops);

-- Create index for document_id lookup
CREATE INDEX IF NOT EXISTS idx_document_embeddings_doc_id 
ON document_embeddings (document_id);
```

**Index Types Comparison:**

| Index Type | Pros | Cons | Best For |
|------------|------|------|----------|
| **HNSW** | Fast search, good recall | Higher memory usage | Most use cases |
| **IVFFlat** | Lower memory, fast build | Slightly lower recall | Memory-constrained |

**Recommended Models:**
- `sentence-transformers/all-MiniLM-L6-v2` (384 dim, good balance)
- `sentence-transformers/all-mpnet-base-v2` (768 dim, higher quality)
- `BAAI/bge-small-en-v1.5` (384 dim, multilingual)

# Security
SECRET_KEY=your_generated_secret_key_here
MCP_API_KEYS=api_key_1,api_key_2,api_key_3

# CORS
ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# Storage
S3_ACCESS_KEY=minio_admin
S3_SECRET_KEY=minio_password
S3_BUCKET=metamorph-prod
```

### Production vs Staging

- **Production**: Use `.env.production` with restrictive settings
- **Staging**: Use `.env.staging` with more permissive settings for testing

## Docker Deployment

### 1. Build and Start Services

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### 2. Verify Services

```bash
docker compose ps
```

### 3. Check Logs

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### 4. Health Checks

```bash
# Backend health check
curl -f http://localhost:8000/health

# Frontend health check  
curl -f http://localhost:3000
```

## Kubernetes Deployment

### 1. Prepare Kubernetes Manifests

Create `k8s/` directory with deployment manifests:

```bash
mkdir -p k8s
# Add your Kubernetes YAML files here
```

### 2. Deploy to Kubernetes

```bash
kubectl apply -f k8s/
```

### 3. Verify Deployment

```bash
kubectl get pods
kubectl get services
```

## CI/CD Pipeline

### GitHub Actions

The repository includes a comprehensive GitHub Actions workflow (`.github/workflows/test-and-deploy.yml`) that:

1. **Runs tests**: Unit, integration, contract, and E2E tests
2. **Builds Docker images**: Creates production-ready images
3. **Deploys to production**: Pushes images and deploys
4. **Generates reports**: Test coverage and deployment summaries

### Manual Deployment

For manual deployments:

```bash
# Build images
docker build -t metamorph-backend -f backend/Dockerfile .
docker build -t metamorph-frontend -f frontend/Dockerfile .

# Push to registry
docker tag metamorph-backend your-registry/metamorph-backend:latest
docker tag metamorph-frontend your-registry/metamorph-frontend:latest
docker push your-registry/metamorph-backend:latest
docker push your-registry/metamorph-frontend:latest

# Deploy
docker compose pull
docker compose up -d
```

## Monitoring and Logging

### Built-in Monitoring

The system includes:

- **Prometheus metrics**: `/metrics` endpoint
- **Health checks**: `/health` endpoint
- **OpenTelemetry tracing**: Integrated with Jaeger
- **Structured logging**: JSON format logs

### Log Rotation

Configure log rotation for production:

```bash
# Add to /etc/logrotate.d/metamorph
/var/log/metamorph/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

## Scaling and Performance

### Horizontal Scaling

Scale backend workers:

```bash
docker compose up -d --scale backend=4
```

### Database Optimization

```sql
-- Add indexes for performance
CREATE INDEX idx_discovered_files_website_id ON discovered_files(website_id);
CREATE INDEX idx_ingestion_jobs_status ON ingestion_jobs(status);
```

### Caching Strategy

Configure Redis caching:

```env
# In your .env file
REDIS_URL=redis://redis:6379/0
CACHE_TTL=3600
CACHE_SIZE_LIMIT=10000
```

## Troubleshooting

### Common Issues

**Database connection failures**:
- Verify PostgreSQL is running
- Check connection string in `.env`
- Test connection: `psql -h localhost -U metamorph_user -d metamorph_prod`

**Frontend not loading**:
- Check Nginx configuration
- Verify API proxy settings
- Test backend endpoint: `curl http://localhost:8000/api/health`

**File upload failures**:
- Check MinIO/S3 credentials
- Verify bucket exists
- Test storage connection

### Debugging Commands

```bash
# Check container logs
docker compose logs backend

# Enter container for debugging
docker compose exec backend bash

# Test database connection
docker compose exec backend python -c "from app.database import engine; print(engine.connect())"
```

## Security Considerations

### Production Security Checklist

- [ ] Use HTTPS with valid certificates
- [ ] Rotate all secrets and API keys
- [ ] Enable firewall rules
- [ ] Set up regular backups
- [ ] Configure monitoring and alerts
- [ ] Enable rate limiting
- [ ] Set up proper CORS policies
- [ ] Enable CSRF protection
- [ ] Configure security headers
- [ ] Set up regular security scans

### Security Headers

The application includes comprehensive security headers:

```
Content-Security-Policy: default-src 'self'
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Referrer-Policy: no-referrer-when-downgrade
```

## Maintenance

### Backups

### Database Setup

**PostgreSQL with pgvector:**

```bash
# Start PostgreSQL container with pgvector pre-installed
docker run -d \
  --name postgres \
  -e POSTGRES_USER=metamorph_user \
  -e POSTGRES_PASSWORD=your_strong_password \
  -e POSTGRES_DB=metamorph_prod \
  -p 5432:5432 \
  -v pg_data:/var/lib/postgresql/data \
  ankane/pgvector:0.5.1

# Connect and enable pgvector extension
psql -h localhost -U metamorph_user -d metamorph_prod -c "CREATE EXTENSION vector;"
```

Regular backup strategy:

```bash
# Database backup (includes vector data)
docker exec postgres pg_dump -U metamorph_user metamorph_prod > backup.sql

# MinIO data backup
docker exec minio mc mirror minio/data backup/minio/
```

### Updates

Update procedure:

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker compose down
docker compose up -d --build

# Run migrations (if any)
docker compose exec backend alembic upgrade head
```

## Support

For issues and support:

- **Documentation**: Check the Wiki.js instance
- **Issues**: Open GitHub issues
- **Community**: Join our Discord/Slack channel
- **Enterprise Support**: Contact support@metamorph.example.com

## License

This deployment guide is provided under the same license as the Metamorph project.
