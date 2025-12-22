# Kubernetes Deployment Guide - Phase V Todo App

## Quick Start (5 Minutes)

### Prerequisites
- [x] Kubernetes cluster running (Minikube, Docker Desktop, or cloud provider)
- [x] kubectl installed and configured
- [x] Helm 3.x installed
- [x] Docker images built: `todo-backend:v3` and `todo-frontend:v1`

### Step 1: Install Dapr on Kubernetes

```bash
# Install Dapr CLI (if not installed)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on your Kubernetes cluster
dapr init -k

# Verify installation
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
dapr-dashboard         dapr-system  True     Running  1         0.14.0   10s  2025-12-20 10:00.00
dapr-sidecar-injector  dapr-system  True     Running  1         1.13.0   10s  2025-12-20 10:00.00
dapr-sentry            dapr-system  True     Running  1         1.13.0   10s  2025-12-20 10:00.00
dapr-operator          dapr-system  True     Running  1         1.13.0   10s  2025-12-20 10:00.00
dapr-placement         dapr-system  True     Running  1         1.13.0   10s  2025-12-20 10:00.00
```

### Step 2: Build Docker Images

```bash
# Navigate to project root
cd "D:\Panavirsty\Phase 51\Todo-Chat-Bot"

# Build backend
cd backend
docker build -t todo-backend:v3 .

# Build frontend
cd ../frontend
docker build -t todo-frontend:v1 .

# Verify images
docker images | grep todo
```

### Step 3: Deploy with Helm

```bash
# Create namespace
kubectl create namespace todo-app

# Install the Helm chart
helm install todo-app ./charts/todo-app -n todo-app

# Watch deployment progress
kubectl get pods -n todo-app -w
```

Wait until all pods show `READY 2/2` (backend/frontend) or `1/1` (postgres/kafka):
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-xxxxx-xxxxx         2/2     Running   0          2m
frontend-xxxxx-xxxxx        2/2     Running   0          2m
postgres-xxxxx-xxxxx        1/1     Running   0          2m
kafka-xxxxx-xxxxx           1/1     Running   0          2m
```

### Step 4: Access the Application

```bash
# Get frontend NodePort
kubectl get svc frontend -n todo-app

# If using Minikube
minikube service frontend -n todo-app

# If using Docker Desktop or cloud provider
# Access at: http://localhost:30080 or http://<NODE_IP>:30080
```

### Step 5: Verify Phase V Features

```bash
# Check Dapr components are loaded
kubectl get components -n todo-app

# Expected output:
# NAME             AGE
# reminder-cron    2m
# todo-pubsub      2m

# Check backend logs for event publishing
kubectl logs -f deployment/backend -n todo-app -c backend | grep "Published"

# Check reminder cron is triggering
kubectl logs -f deployment/backend -n todo-app -c backend | grep "Reminder cron triggered"
```

## Detailed Deployment Steps

### Option 1: Using Minikube (Local Development)

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable ingress addon (optional)
minikube addons enable ingress

# Install Dapr
dapr init -k

# Build images and load into Minikube
eval $(minikube docker-env)
cd backend && docker build -t todo-backend:v3 .
cd ../frontend && docker build -t todo-frontend:v1 .

# Deploy
helm install todo-app ./charts/todo-app -n todo-app

# Access services
minikube service frontend -n todo-app
```

### Option 2: Using Docker Desktop Kubernetes

```bash
# Enable Kubernetes in Docker Desktop settings

# Build images (they're automatically available in the cluster)
cd backend && docker build -t todo-backend:v3 .
cd ../frontend && docker build -t todo-frontend:v1 .

# Install Dapr
dapr init -k

# Deploy
kubectl create namespace todo-app
helm install todo-app ./charts/todo-app -n todo-app

# Access at http://localhost:30080
```

### Option 3: Using Cloud Provider (GKE, EKS, AKS)

```bash
# Connect to your cluster
# GKE: gcloud container clusters get-credentials CLUSTER_NAME
# EKS: aws eks update-kubeconfig --name CLUSTER_NAME
# AKS: az aks get-credentials --resource-group RG --name CLUSTER_NAME

# Push images to container registry
docker tag todo-backend:v3 YOUR_REGISTRY/todo-backend:v3
docker push YOUR_REGISTRY/todo-backend:v3

docker tag todo-frontend:v1 YOUR_REGISTRY/todo-frontend:v1
docker push YOUR_REGISTRY/todo-frontend:v1

# Update values.yaml with registry URLs
# backend.image.repository: YOUR_REGISTRY/todo-backend
# frontend.image.repository: YOUR_REGISTRY/todo-frontend

# Install Dapr
dapr init -k

# Deploy
kubectl create namespace todo-app
helm install todo-app ./charts/todo-app -n todo-app -f production-values.yaml

# Get LoadBalancer IP (if using LoadBalancer service type)
kubectl get svc frontend -n todo-app
```

## Architecture in Kubernetes

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Namespace: todo-app                    │    │
│  │                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐              │    │
│  │  │   Backend    │  │   Frontend   │               │    │
│  │  │  Deployment  │  │  Deployment  │               │    │
│  │  │              │  │              │               │    │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │              │    │
│  │  │ │  App     │ │  │ │  App     │ │               │    │
│  │  │ │Container │ │  │ │Container │ │               │    │
│  │  │ └──────────┘ │  │ └──────────┘ │              │    │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │              │    │
│  │  │ │  Dapr    │ │  │ │  Dapr    │ │               │    │
│  │  │ │ Sidecar  │ │  │ │ Sidecar  │ │               │    │
│  │  │ └──────────┘ │  │ └──────────┘ │              │    │
│  │  └──────────────┘  └──────────────┘               │    │
│  │         │                  │                       │    │
│  │         │                  │                       │    │
│  │  ┌──────▼──────┐    ┌─────▼──────┐              │    │
│  │  │  Service    │    │  Service   │               │    │
│  │  │ (ClusterIP) │    │ (NodePort) │               │    │
│  │  └─────────────┘    └────────────┘               │    │
│  │         │                                          │    │
│  │         │                                          │    │
│  │  ┌──────▼──────────────────────────────┐        │    │
│  │  │     Dapr Components                  │         │    │
│  │  │  ┌────────────┐  ┌──────────────┐  │         │    │
│  │  │  │ todo-pubsub│  │reminder-cron │   │         │    │
│  │  │  │  (Kafka)   │  │   (Cron)     │   │         │    │
│  │  │  └────────────┘  └──────────────┘  │         │    │
│  │  └───────────────────────────────────────┘        │    │
│  │         │                                          │    │
│  │         │                                          │    │
│  │  ┌──────▼──────┐    ┌──────────────┐            │    │
│  │  │   Kafka     │    │  PostgreSQL  │             │    │
│  │  │ Deployment  │    │  Deployment  │             │    │
│  │  └─────────────┘    └──────────────┘            │    │
│  │         │                    │                    │    │
│  │  ┌──────▼──────┐    ┌───────▼──────┐           │    │
│  │  │  kafka-pvc  │    │ postgres-pvc │            │    │
│  │  │   (10Gi)    │    │    (10Gi)    │            │    │
│  │  └─────────────┘    └──────────────┘            │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Verifying Deployment

### Check All Resources

```bash
# All pods should be Running
kubectl get pods -n todo-app

# All services should have endpoints
kubectl get svc -n todo-app

# Dapr components should be present
kubectl get components -n todo-app

# Check deployments
kubectl get deployments -n todo-app

# Check PVCs
kubectl get pvc -n todo-app
```

### Test API Endpoints

```bash
# Port-forward backend
kubectl port-forward svc/backend 8000:8000 -n todo-app

# In another terminal, test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/

# Test authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "demo@example.com", "password": "demo123"}'
```

### Monitor Logs

```bash
# Backend application logs
kubectl logs -f deployment/backend -n todo-app -c backend

# Backend Dapr sidecar logs
kubectl logs -f deployment/backend -n todo-app -c daprd

# Frontend logs
kubectl logs -f deployment/frontend -n todo-app -c frontend

# Kafka logs
kubectl logs -f deployment/kafka -n todo-app

# PostgreSQL logs
kubectl logs -f deployment/postgres -n todo-app
```

## Configuration Management

### Update Image Versions

```bash
# Update values.yaml
# backend.image.tag: v4

# Upgrade deployment
helm upgrade todo-app ./charts/todo-app -n todo-app

# Check rollout status
kubectl rollout status deployment/backend -n todo-app
```

### Scale Services

```bash
# Scale backend replicas
helm upgrade todo-app ./charts/todo-app -n todo-app \
  --set backend.replicaCount=5

# Or use kubectl
kubectl scale deployment backend --replicas=5 -n todo-app
```

### Update Environment Variables

```bash
# Edit values.yaml, then upgrade
helm upgrade todo-app ./charts/todo-app -n todo-app

# Or patch directly
kubectl set env deployment/backend \
  DATABASE_URL="postgresql://newuser:newpass@postgres:5432/tododb" \
  -n todo-app
```

## Troubleshooting

### Pods Stuck in Pending

```bash
# Check events
kubectl describe pod <pod-name> -n todo-app

# Common causes:
# - Insufficient resources
# - PVC not bound
# - Image pull errors
```

### Dapr Sidecar Not Injecting

```bash
# Verify Dapr is running
dapr status -k

# Check namespace has Dapr enabled
kubectl get namespace todo-app -o yaml

# Enable if needed
kubectl label namespace todo-app dapr.io/enabled=true

# Restart pods
kubectl rollout restart deployment/backend -n todo-app
```

### Cannot Access Frontend

```bash
# Check NodePort service
kubectl get svc frontend -n todo-app

# Check pod is ready
kubectl get pods -l app=frontend -n todo-app

# Check logs
kubectl logs -f deployment/frontend -n todo-app -c frontend

# Test with port-forward
kubectl port-forward svc/frontend 3000:3000 -n todo-app
```

### Events Not Publishing

```bash
# Check Kafka is running
kubectl get pods -l app=kafka -n todo-app

# Check Dapr pub/sub component
kubectl describe component todo-pubsub -n todo-app

# Check backend Dapr logs
kubectl logs -f deployment/backend -n todo-app -c daprd

# Test Kafka connectivity
kubectl exec -it deployment/backend -n todo-app -c backend -- \
  curl http://localhost:3500/v1.0/publish/todo-pubsub/task-events
```

## Cleanup

```bash
# Uninstall Helm release
helm uninstall todo-app -n todo-app

# Delete PVCs (optional - this deletes data!)
kubectl delete pvc --all -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Uninstall Dapr (optional)
dapr uninstall -k
```

## Production Considerations

### Security
- [ ] Use Kubernetes secrets for sensitive data
- [ ] Enable TLS/SSL for external access
- [ ] Configure network policies
- [ ] Use private container registry
- [ ] Enable RBAC

### High Availability
- [ ] Run multiple replicas (backend, frontend)
- [ ] Use StatefulSet for Kafka and PostgreSQL
- [ ] Configure pod disruption budgets
- [ ] Set up health checks and readiness probes

### Monitoring
- [ ] Deploy Prometheus and Grafana
- [ ] Configure Dapr metrics collection
- [ ] Set up log aggregation (ELK, Loki)
- [ ] Configure alerting rules

### Backup & Recovery
- [ ] Set up database backups
- [ ] Configure PVC snapshots
- [ ] Document disaster recovery procedures

## Next Steps

1. **Set up Ingress** for external access with custom domain
2. **Configure autoscaling** (HPA) based on CPU/memory
3. **Add monitoring** with Prometheus and Grafana
4. **Set up CI/CD** pipeline for automated deployments
5. **Configure logging** aggregation
6. **Implement secrets management** with Vault or cloud provider

## Support

For issues:
1. Check pod logs: `kubectl logs -f deployment/backend -n todo-app`
2. Review events: `kubectl get events -n todo-app --sort-by='.lastTimestamp'`
3. Check Dapr dashboard: `dapr dashboard -k`
4. Review Helm values: `helm get values todo-app -n todo-app`

For more details, see `charts/todo-app/README.md`
