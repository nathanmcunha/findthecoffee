# Coffee Finder - Kubernetes Deployment

This directory contains the manifests to deploy the Coffee Finder application to a Kubernetes cluster.

## Architecture
- **Namespace**: `coffee-finder`
- **Database**: PostgreSQL 16 (internal)
- **Backend**: Flask REST API (ClusterIP)
- **Frontend**: Nginx static UI (NodePort: 30080)

## Deployment Steps

### 1. Build & Load Images
Before applying the manifests, you must build the backend and frontend images. If you are using a local cluster like `kind` or `minikube`, ensure you load them into the cluster's internal registry.

```bash
# Build Backend
podman build -t coffee-backend:latest ./backend

# Build Frontend
podman build -t coffee-frontend:latest ./frontend

# (If using kind) Load images
kind load docker-image coffee-backend:latest
kind load docker-image coffee-frontend:latest
```

### 2. Apply Manifests
Apply the manifests in order:

```bash
# 1. Create Namespace
kubectl apply -f k8s/00-namespace.yaml

# 2. Setup Config & Secrets
kubectl apply -f k8s/00-config.yaml

# 3. Deploy Database
kubectl apply -f k8s/01-database.yaml

# 4. Deploy Backend & Frontend
kubectl apply -f k8s/02-backend.yaml
kubectl apply -f k8s/03-frontend.yaml
```

### 3. Access the Application
The frontend is exposed via a NodePort on port **30080**.

- **Minikube**: `minikube service frontend -n coffee-finder --url`
- **Kind/Direct**: `http://localhost:30080` (if port-forwarding is configured)

## Management

### Check Status
```bash
kubectl get all -n coffee-finder
```

### View Logs
```bash
# Backend Logs
kubectl logs -l app=backend -n coffee-finder -f

# Database Logs
kubectl logs -l app=db -n coffee-finder -f
```

### Clean Up
```bash
kubectl delete -f k8s/
```
