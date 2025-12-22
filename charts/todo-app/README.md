# Todo-App Helm Chart

This Helm chart deploys the Todo Chat Bot application with Dapr support on Kubernetes.

## Overview

This chart deploys:
- **Backend Service** (FastAPI) with Dapr sidecar
- **Frontend Service** (Next.js) with Dapr sidecar
- **PostgreSQL Database** for data persistence
- **Kafka** for event-driven messaging
- **Dapr Components** (pub/sub and cron bindings)

## Prerequisites

- Kubernetes cluster (v1.24+)
- Helm 3.x installed
- kubectl configured to access your cluster
- Dapr installed on Kubernetes cluster

## Installing Dapr on Kubernetes

If Dapr is not already installed on your cluster:

```bash
# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init -k

# Verify Dapr installation
dapr status -k
```

Expected output:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE  CREATED
dapr-dashboard         dapr-system  True     Running  1         0.14.0   15s  2025-12-20 10:00.00
dapr-sidecar-injector  dapr-system  True     Running  1         1.13.0   15s  2025-12-20 10:00.00
dapr-sentry            dapr-system  True     Running  1         1.13.0   15s  2025-12-20 10:00.00
dapr-operator          dapr-system  True     Running  1         1.13.0   15s  2025-12-20 10:00.00
dapr-placement         dapr-system  True     Running  1         1.13.0   15s  2025-12-20 10:00.00
```

## Installation

### 1. Build Docker Images

First, build and tag your Docker images:

```bash
# Build backend image
cd backend
docker build -t todo-backend:v3 .

# Build frontend image
cd ../frontend
docker build -t todo-frontend:v1 .

# If using a private registry, tag and push
docker tag todo-backend:v3 YOUR_REGISTRY/todo-backend:v3
docker push YOUR_REGISTRY/todo-backend:v3

docker tag todo-frontend:v1 YOUR_REGISTRY/todo-frontend:v1
docker push YOUR_REGISTRY/todo-frontend:v1
```

### 2. Update values.yaml

Edit `values.yaml` to configure your deployment:

```yaml
backend:
  image:
    repository: YOUR_REGISTRY/todo-backend  # Update if using private registry
    tag: v3

frontend:
  image:
    repository: YOUR_REGISTRY/todo-frontend  # Update if using private registry
    tag: v1

# Update database credentials
postgresql:
  env:
    - name: POSTGRES_PASSWORD
      value: "YOUR_SECURE_PASSWORD"  # Change this!
```

### 3. Install the Chart

```bash
# Create namespace
kubectl create namespace todo-app

# Install with Helm
helm install todo-app ./charts/todo-app -n todo-app

# Or install with custom values
helm install todo-app ./charts/todo-app -n todo-app -f custom-values.yaml
```

### 4. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n todo-app

# Expected output:
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-xxxxx-xxxxx         2/2     Running   0          2m
# frontend-xxxxx-xxxxx        2/2     Running   0          2m
# postgres-xxxxx-xxxxx        1/1     Running   0          2m
# kafka-xxxxx-xxxxx           1/1     Running   0          2m

# Note: Backend and frontend show 2/2 because of Dapr sidecar

# Check services
kubectl get svc -n todo-app

# Check Dapr components
kubectl get components -n todo-app
```

## Accessing the Application

### Frontend (NodePort)

```bash
# Get the NodePort
kubectl get svc frontend -n todo-app

# Access via browser
# If using Minikube:
minikube service frontend -n todo-app

# If using cloud provider:
http://<NODE_IP>:30080
```

### Backend API

The backend is exposed as ClusterIP (internal only). To access for testing:

```bash
# Port-forward the backend service
kubectl port-forward svc/backend 8000:8000 -n todo-app

# Access API docs
open http://localhost:8000/docs
```

## Configuration

### Image Configuration

Edit `values.yaml`:

```yaml
backend:
  image:
    repository: todo-backend
    tag: v3
    pullPolicy: IfNotPresent

frontend:
  image:
    repository: todo-frontend
    tag: v1
    pullPolicy: IfNotPresent
```

### Scaling

Edit `values.yaml` to adjust replica counts:

```yaml
backend:
  replicaCount: 3  # Scale backend to 3 replicas

frontend:
  replicaCount: 2  # Scale frontend to 2 replicas
```

Apply changes:
```bash
helm upgrade todo-app ./charts/todo-app -n todo-app
```

### Resource Limits

Adjust resource limits in `values.yaml`:

```yaml
backend:
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
```

### Database Configuration

To use an external PostgreSQL database:

```yaml
postgresql:
  enabled: false  # Disable built-in PostgreSQL

backend:
  env:
    - name: DATABASE_URL
      value: "postgresql://user:pass@external-db:5432/tododb"
```

### Kafka Configuration

To use an external Kafka cluster:

```yaml
kafka:
  enabled: false  # Disable built-in Kafka

dapr:
  components:
    pubsub:
      metadata:
        - name: brokers
          value: "external-kafka:9092"
```

## Dapr Configuration

### Pub/Sub Component

The chart creates a Dapr pub/sub component for Kafka:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.kafka
  metadata:
  - name: brokers
    value: "kafka:9092"
```

Topics used:
- `task-events` - Task lifecycle events (created, updated, completed)
- `reminders` - Task reminder notifications

### Cron Binding Component

The chart creates a Dapr cron binding for reminders:

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  metadata:
  - name: schedule
    value: "* * * * *"  # Every minute
```

### Dapr Annotations

Both backend and frontend deployments include Dapr annotations:

**Backend:**
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "backend"
  dapr.io/app-port: "8000"
  dapr.io/http-port: "3500"
  dapr.io/grpc-port: "50001"
```

**Frontend:**
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "frontend"
  dapr.io/app-port: "3000"
  dapr.io/http-port: "3501"
  dapr.io/grpc-port: "50002"
```

## Monitoring

### View Logs

```bash
# Backend logs (app + Dapr sidecar)
kubectl logs -f deployment/backend -n todo-app -c backend
kubectl logs -f deployment/backend -n todo-app -c daprd

# Frontend logs
kubectl logs -f deployment/frontend -n todo-app -c frontend
kubectl logs -f deployment/frontend -n todo-app -c daprd

# Kafka logs
kubectl logs -f deployment/kafka -n todo-app

# PostgreSQL logs
kubectl logs -f deployment/postgres -n todo-app
```

### Dapr Dashboard

```bash
# Access Dapr dashboard
dapr dashboard -k -p 9999

# Open browser to http://localhost:9999
```

### Health Checks

```bash
# Backend health
kubectl exec -it deployment/backend -n todo-app -- curl http://localhost:8000/health

# Frontend health
kubectl exec -it deployment/frontend -n todo-app -- curl http://localhost:3000
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n todo-app

# Common issues:
# 1. Image pull errors - verify image exists and registry access
# 2. Resource constraints - check node resources
# 3. Dapr not installed - run: dapr status -k
```

### Dapr Sidecar Not Injected

```bash
# Verify Dapr is running
dapr status -k

# Check if namespace has Dapr enabled
kubectl get namespace todo-app -o yaml | grep dapr

# Enable Dapr for namespace
kubectl label namespace todo-app dapr.io/enabled=true
```

### Events Not Publishing

```bash
# Check Dapr components
kubectl get components -n todo-app

# Check component logs
kubectl logs -l app=backend -n todo-app -c daprd

# Verify Kafka is running
kubectl get pods -n todo-app | grep kafka
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
kubectl get pods -n todo-app | grep postgres

# Test connection from backend
kubectl exec -it deployment/backend -n todo-app -- \
  curl http://localhost:8000/health

# Check database URL environment variable
kubectl exec -it deployment/backend -n todo-app -- \
  env | grep DATABASE_URL
```

## Upgrading

```bash
# Upgrade to new version
helm upgrade todo-app ./charts/todo-app -n todo-app

# Upgrade with new values
helm upgrade todo-app ./charts/todo-app -n todo-app -f new-values.yaml

# Rollback if needed
helm rollback todo-app -n todo-app
```

## Uninstalling

```bash
# Uninstall the chart
helm uninstall todo-app -n todo-app

# Clean up PVCs (if needed)
kubectl delete pvc -n todo-app --all

# Delete namespace
kubectl delete namespace todo-app
```

## Advanced Configuration

### Using Ingress

Add an Ingress resource for external access:

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-app-ingress
  namespace: todo-app
  annotations:
    kubernetes.io/ingress.class: nginx
spec:
  rules:
  - host: todo-app.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend
            port:
              number: 3000
```

Apply:
```bash
kubectl apply -f ingress.yaml
```

### Using Secrets

Store sensitive data in Kubernetes secrets:

```bash
# Create database secret
kubectl create secret generic db-credentials \
  --from-literal=username=user \
  --from-literal=password=secret123 \
  -n todo-app

# Update values.yaml to use secret
backend:
  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: connection-string
```

### Horizontal Pod Autoscaling

Enable HPA for automatic scaling:

```bash
# Create HPA for backend
kubectl autoscale deployment backend \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n todo-app

# Check HPA status
kubectl get hpa -n todo-app
```

## Testing Phase V Features

Once deployed, test the Phase V features:

### 1. Test Event-Driven Updates

```bash
# Port-forward backend
kubectl port-forward svc/backend 8000:8000 -n todo-app

# Create a task (publishes task.created event)
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task"}'

# Check backend logs for event publishing
kubectl logs -f deployment/backend -n todo-app -c backend | grep "Published"
```

### 2. Test Recurring Tasks

```bash
# Create recurring task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title": "Daily Task", "recurrence": "daily"}'

# Complete it
curl -X PUT http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"status": "completed"}'

# Wait 3 seconds and list tasks - should see new instance
kubectl logs -f deployment/backend -n todo-app -c backend | grep "recurring"
```

### 3. Test Reminder System

```bash
# Check cron is running
kubectl logs -f deployment/backend -n todo-app -c daprd | grep "reminder-cron"

# Check backend for reminder logs
kubectl logs -f deployment/backend -n todo-app -c backend | grep "Sending Reminder"
```

## Support

For issues or questions:
- Check logs: `kubectl logs -f deployment/backend -n todo-app`
- Review Dapr logs: `kubectl logs -f deployment/backend -n todo-app -c daprd`
- Visit Dapr documentation: https://docs.dapr.io/

## License

Copyright © 2025 Todo App Team
