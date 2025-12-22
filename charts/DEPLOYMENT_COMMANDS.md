# Deployment Commands Quick Reference

## Prerequisites Setup

```bash
# Install Dapr CLI (Linux/Mac)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Install Dapr CLI (Windows - PowerShell as Admin)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Verify Dapr installation
dapr version

# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr is running
dapr status -k
```

## Build Images

```bash
# Navigate to project root
cd "D:\Panavirsty\Phase 51\Todo-Chat-Bot"

# Build backend image
cd backend
docker build -t todo-backend:v3 .

# Build frontend image
cd ../frontend
docker build -t todo-frontend:v1 .

# Verify images
docker images | grep todo
```

## Deploy to Minikube

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Use Minikube's Docker daemon
eval $(minikube docker-env)

# Build images in Minikube
cd backend && docker build -t todo-backend:v3 .
cd ../frontend && docker build -t todo-frontend:v1 .

# Create namespace
kubectl create namespace todo-app

# Deploy with development values
helm install todo-app ./charts/todo-app \
  -n todo-app \
  -f ./charts/todo-app/values-development.yaml

# Access frontend
minikube service frontend -n todo-app
```

## Deploy to Docker Desktop

```bash
# Build images (automatically available in cluster)
docker build -t todo-backend:v3 ./backend
docker build -t todo-frontend:v1 ./frontend

# Create namespace
kubectl create namespace todo-app

# Deploy
helm install todo-app ./charts/todo-app -n todo-app

# Access frontend
# Open browser to: http://localhost:30080
```

## Deploy to Cloud (GKE/EKS/AKS)

```bash
# Tag images for registry
docker tag todo-backend:v3 gcr.io/PROJECT_ID/todo-backend:v3
docker tag todo-frontend:v1 gcr.io/PROJECT_ID/todo-frontend:v1

# Push to registry
docker push gcr.io/PROJECT_ID/todo-backend:v3
docker push gcr.io/PROJECT_ID/todo-frontend:v1

# Update values-production.yaml with registry URLs

# Create namespace
kubectl create namespace todo-app

# Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=auth-secret='your-secret-key' \
  --from-literal=database-url='postgresql://user:pass@host:5432/db' \
  -n todo-app

# Create registry credentials (if private)
kubectl create secret docker-registry registry-credentials \
  --docker-server=gcr.io \
  --docker-username=_json_key \
  --docker-password="$(cat key.json)" \
  -n todo-app

# Deploy with production values
helm install todo-app ./charts/todo-app \
  -n todo-app \
  -f ./charts/todo-app/values-production.yaml

# Get LoadBalancer IP
kubectl get svc frontend -n todo-app
```

## Verification Commands

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxxxx-xxxxx         2/2     Running   0          2m
# frontend-xxxxx-xxxxx        2/2     Running   0          2m
# postgres-xxxxx-xxxxx        1/1     Running   0          2m
# kafka-xxxxx-xxxxx           1/1     Running   0          2m

# Check services
kubectl get svc -n todo-app

# Check Dapr components
kubectl get components -n todo-app

# Check deployments
kubectl get deployments -n todo-app

# Check PVCs
kubectl get pvc -n todo-app
```

## Monitoring Commands

```bash
# View backend logs (application)
kubectl logs -f deployment/backend -n todo-app -c backend

# View backend logs (Dapr sidecar)
kubectl logs -f deployment/backend -n todo-app -c daprd

# View frontend logs
kubectl logs -f deployment/frontend -n todo-app -c frontend

# View Kafka logs
kubectl logs -f deployment/kafka -n todo-app

# View PostgreSQL logs
kubectl logs -f deployment/postgres -n todo-app

# View all events
kubectl get events -n todo-app --sort-by='.lastTimestamp'

# Describe a pod (for troubleshooting)
kubectl describe pod <pod-name> -n todo-app
```

## Testing Commands

```bash
# Port-forward backend API
kubectl port-forward svc/backend 8000:8000 -n todo-app

# Test health endpoint
curl http://localhost:8000/health

# Test API docs
open http://localhost:8000/docs

# Port-forward frontend
kubectl port-forward svc/frontend 3000:3000 -n todo-app

# Access frontend
open http://localhost:3000
```

## Configuration Updates

```bash
# Update image version
helm upgrade todo-app ./charts/todo-app -n todo-app \
  --set backend.image.tag=v4

# Scale backend replicas
helm upgrade todo-app ./charts/todo-app -n todo-app \
  --set backend.replicaCount=5

# Change frontend service type to LoadBalancer
helm upgrade todo-app ./charts/todo-app -n todo-app \
  --set frontend.service.type=LoadBalancer

# Update environment variable
helm upgrade todo-app ./charts/todo-app -n todo-app \
  --set backend.env[0].name=LOG_LEVEL \
  --set backend.env[0].value=debug

# Upgrade with new values file
helm upgrade todo-app ./charts/todo-app -n todo-app \
  -f ./charts/todo-app/values-production.yaml
```

## Scaling Commands

```bash
# Manual scaling
kubectl scale deployment backend --replicas=5 -n todo-app
kubectl scale deployment frontend --replicas=3 -n todo-app

# Auto-scaling (HPA)
kubectl autoscale deployment backend \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n todo-app

# Check HPA status
kubectl get hpa -n todo-app
```

## Rollout Management

```bash
# Check rollout status
kubectl rollout status deployment/backend -n todo-app

# View rollout history
kubectl rollout history deployment/backend -n todo-app

# Rollback to previous version
kubectl rollout undo deployment/backend -n todo-app

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n todo-app

# Pause rollout
kubectl rollout pause deployment/backend -n todo-app

# Resume rollout
kubectl rollout resume deployment/backend -n todo-app

# Restart deployment (zero downtime)
kubectl rollout restart deployment/backend -n todo-app
```

## Helm Management

```bash
# List all releases
helm list -n todo-app

# Get release values
helm get values todo-app -n todo-app

# Get release manifest
helm get manifest todo-app -n todo-app

# Upgrade release
helm upgrade todo-app ./charts/todo-app -n todo-app

# Rollback release
helm rollback todo-app -n todo-app

# Rollback to specific revision
helm rollback todo-app 1 -n todo-app

# Show release history
helm history todo-app -n todo-app

# Uninstall release
helm uninstall todo-app -n todo-app
```

## Debug Commands

```bash
# Execute command in pod
kubectl exec -it deployment/backend -n todo-app -c backend -- /bin/bash

# Execute command in Dapr sidecar
kubectl exec -it deployment/backend -n todo-app -c daprd -- /bin/sh

# Copy files from pod
kubectl cp todo-app/backend-xxxxx:/app/logs.txt ./logs.txt -c backend

# Check pod resource usage
kubectl top pods -n todo-app

# Check node resource usage
kubectl top nodes

# Get pod details in YAML
kubectl get pod backend-xxxxx -n todo-app -o yaml

# Check Dapr subscription endpoints
kubectl exec -it deployment/backend -n todo-app -c backend -- \
  curl http://localhost:3500/dapr/subscribe

# Test Dapr pub/sub
kubectl exec -it deployment/backend -n todo-app -c backend -- \
  curl -X POST http://localhost:3500/v1.0/publish/todo-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

## Dapr-Specific Commands

```bash
# Check Dapr status in cluster
dapr status -k

# View Dapr dashboard
dapr dashboard -k -p 9999
# Then open: http://localhost:9999

# List Dapr components in namespace
kubectl get components -n todo-app

# Describe Dapr component
kubectl describe component todo-pubsub -n todo-app

# View Dapr logs
kubectl logs -l app.kubernetes.io/name=dapr -n dapr-system

# Check Dapr sidecar injection
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].name}{"\n"}{end}'
```

## Cleanup Commands

```bash
# Delete specific resources
kubectl delete deployment backend -n todo-app
kubectl delete svc backend -n todo-app

# Uninstall Helm release (keeps PVCs)
helm uninstall todo-app -n todo-app

# Delete PVCs (CAUTION: deletes data!)
kubectl delete pvc --all -n todo-app

# Delete namespace (deletes everything)
kubectl delete namespace todo-app

# Uninstall Dapr from cluster
dapr uninstall -k

# Delete Dapr namespace
kubectl delete namespace dapr-system
```

## Backup Commands

```bash
# Backup PostgreSQL data
kubectl exec -it deployment/postgres -n todo-app -- \
  pg_dump -U user tododb > backup.sql

# Restore PostgreSQL data
cat backup.sql | kubectl exec -i deployment/postgres -n todo-app -- \
  psql -U user tododb

# Export Helm values
helm get values todo-app -n todo-app > backup-values.yaml

# Backup all Kubernetes resources
kubectl get all -n todo-app -o yaml > backup-resources.yaml
```

## Performance Testing

```bash
# Install hey (HTTP load testing tool)
go install github.com/rakyll/hey@latest

# Load test backend
kubectl port-forward svc/backend 8000:8000 -n todo-app
hey -n 1000 -c 10 http://localhost:8000/health

# Load test frontend
hey -n 1000 -c 10 http://localhost:30080
```

## Quick Troubleshooting

```bash
# Pod won't start
kubectl describe pod <pod-name> -n todo-app
kubectl logs <pod-name> -n todo-app --previous

# Dapr sidecar not injecting
kubectl label namespace todo-app dapr.io/enabled=true
kubectl rollout restart deployment/backend -n todo-app

# Service not reachable
kubectl get endpoints -n todo-app
kubectl describe svc <service-name> -n todo-app

# Image pull errors
kubectl describe pod <pod-name> -n todo-app | grep -A 10 Events

# Resource constraints
kubectl describe nodes
kubectl top pods -n todo-app
```

## One-Liner Helpers

```bash
# Get all pod IPs
kubectl get pods -n todo-app -o wide

# Watch pod status
watch kubectl get pods -n todo-app

# Get all container images
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.spec.containers[*].image}{"\n"}{end}'

# Get all environment variables
kubectl exec deployment/backend -n todo-app -c backend -- env

# Check DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -n todo-app -- nslookup backend

# Get all resource requests/limits
kubectl describe nodes | grep -A 5 "Allocated resources"
```

## Complete Deployment Flow

```bash
# 1. Setup
dapr init -k
kubectl create namespace todo-app

# 2. Build & Deploy
docker build -t todo-backend:v3 ./backend
docker build -t todo-frontend:v1 ./frontend
helm install todo-app ./charts/todo-app -n todo-app

# 3. Verify
kubectl get pods -n todo-app -w
kubectl get components -n todo-app

# 4. Access
minikube service frontend -n todo-app
# OR
kubectl port-forward svc/frontend 3000:3000 -n todo-app

# 5. Monitor
kubectl logs -f deployment/backend -n todo-app -c backend
dapr dashboard -k

# 6. Test
curl http://localhost:8000/health

# 7. Cleanup (when done)
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
```
