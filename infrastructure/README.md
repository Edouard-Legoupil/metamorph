# Metamorph Infrastructure Deployment

## Local: Docker Compose

1. Copy `.env.example` to `.env`, set your keys and DB credentials.
2. Build and start with:
```bash
docker compose -f infrastructure/docker-compose.yaml up --build
```
See [../docs/get-started.md](../docs/get-started.md) for troubleshooting tips.

## Kubernetes (GKE/EKS/AKS...)

- See `main.tf`, `k8s/*.yaml`, and customize to your cluster. Apply secrets first, then deployments/services/ingress.
- Recommended:
  * Use managed PostgreSQL and MinIO/S3 buckets for storage and DB.
  * Set all API and agent keys as Kubernetes secrets, mount by env.
  * Only expose port 80/443 for the ingress. All other ports internal.

## Security Warnings
- Never commit real .env/secret values to git.
- MCP_API keys, minio keys, DB credentials must be rotated/regenerated per policy.
- All persistent logs/output are sensitive. Forward to a secure logging system or SIEM in prod.

## Scaling and Monitoring
- Increase `replicas` in main.tf or app.yaml for web/API scaling.
- All logs available from docker/k8s logs or downstream ELK/Timescale/Pg logs.
