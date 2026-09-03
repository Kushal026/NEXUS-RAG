# NEXUS-RAG Production Deployment Guide

## 1. Production Architecture Overview

In production, NEXUS-RAG runs as a containerized microservice cluster behind a reverse proxy (Nginx, Traefik, or AWS ALB) with Redis for caching and Neo4j for persistent knowledge graph storage.

```
                  [ Ingress / TLS Load Balancer (HTTPS:443) ]
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
[ Next.js Frontend Cluster ]                             [ FastAPI Backend Cluster ]
      (Port: 3000)                                              (Port: 8000)
                                                                   |
                                         +-------------------------+-------------------------+
                                         |                                                   |
                                         v                                                   v
                            [ Redis Cache Cluster ]                              [ Neo4j Enterprise Cluster ]
                                  (Port: 6379)                                          (Port: 7687)
```

---

## 2. Docker Compose Deployment

### 2.1 Starting Services

```bash
# Clone the repository
git clone https://github.com/Kushal026/NEXUS-RAG.git
cd NEXUS-RAG

# Launch all production containers
docker-compose up -d --build
```

### 2.2 Verifying Cluster Health

```bash
# Verify Backend Liveness & Readiness
curl http://localhost:8000/health
curl http://localhost:8000/readiness

# Check Prometheus Telemetry Metrics
curl http://localhost:8000/metrics

# Check Container Logs
docker-compose logs -f backend
```

---

## 3. Environment Variables Configuration

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Deployment runtime environment (`production`, `staging`, `development`). |
| `SECRET_KEY` | *(Must be set)* | Cryptographic HMAC key for JWT signing and password encryption. |
| `REDIS_URL` | `redis://redis:6379/0` | Connection URI for the Redis caching cluster. |
| `NEO4J_URI` | `bolt://neo4j:7687` | Bolt protocol connection URI for Neo4j database. |
| `NEO4J_USER` | `neo4j` | Neo4j username. |
| `NEO4J_PASSWORD`| `nexus_graph_password_2026` | Neo4j database password. |
| `MAX_UPLOAD_SIZE_MB` | `50` | Maximum file upload limit for multimodal documents. |

---

## 4. Kubernetes Production Deployment

For enterprise Kubernetes clusters, use the standard deployment manifests with liveness and readiness probes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nexus-rag-backend
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: backend
        image: nexus-rag-backend:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readiness
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```
