# Kubernetes Deployment for AI Support Service

This directory contains Kubernetes manifests for deploying the AI Support Service.

## Files

- **deployment.yaml** - Deployment configuration with 2 replicas
- **service.yaml** - ClusterIP service exposing port 80
- **hpa.yaml** - HorizontalPodAutoscaler for auto-scaling (2-5 replicas)
- **secret.yaml.template** - Template for creating the Groq API key secret

## Prerequisites

1. Kubernetes cluster (v1.19+)
2. kubectl configured to connect to your cluster
3. Groq API key from [console.groq.com](https://console.groq.com/keys)
4. Docker image built and available to your cluster

## Quick Start

### 1. Build and Push Docker Image

```bash
# Build the image
docker build -t ai-support-service:latest .

# Tag for your registry (example for Docker Hub)
docker tag ai-support-service:latest your-username/ai-support-service:latest

# Push to registry
docker push your-username/ai-support-service:latest
```

Update the image reference in [deployment.yaml](deployment.yaml) if using a registry:
```yaml
image: your-username/ai-support-service:latest
```

### 2. Create Secret

```bash
# Copy the template
cp secret.yaml.template secret.yaml

# Edit secret.yaml and add your Groq API key
# Replace "your_groq_api_key_here" with your actual API key

# Create the secret
kubectl apply -f secret.yaml

# Verify
kubectl get secret ai-support-service-secrets
```

**Important:** Add `secret.yaml` to `.gitignore` to avoid committing your API key.

### 3. Deploy the Application

```bash
# Apply all manifests
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

# Or apply all at once
kubectl apply -f .
```

### 4. Verify Deployment

```bash
# Check deployment status
kubectl get deployments
kubectl get pods

# Check service
kubectl get services

# Check HPA
kubectl get hpa

# View logs
kubectl logs -l app=ai-support-service --tail=50 -f

# Check health
kubectl port-forward svc/ai-support-service 8080:80
curl http://localhost:8080/health
```

## Configuration

### Resource Limits

Current configuration:
- **CPU Request**: 100m (0.1 cores)
- **CPU Limit**: 500m (0.5 cores)
- **Memory Request**: 128Mi
- **Memory Limit**: 512Mi

Adjust in [deployment.yaml](deployment.yaml) based on your workload:
```yaml
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

### Auto-scaling

The HPA will scale pods based on CPU utilization:
- **Min Replicas**: 2
- **Max Replicas**: 5
- **Target CPU**: 70%

Monitor scaling:
```bash
kubectl get hpa ai-support-service --watch
```

## Accessing the Service

### From within the cluster

```bash
# DNS name
http://ai-support-service.default.svc.cluster.local
```

### From outside the cluster

#### Option 1: Port Forward (Development)

```bash
kubectl port-forward svc/ai-support-service 8080:80

# Access at http://localhost:8080
curl http://localhost:8080/health
```

#### Option 2: Ingress (Production)

Create an ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-support-service-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: ai-support.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-support-service
            port:
              number: 80
```

Apply:
```bash
kubectl apply -f ingress.yaml
```

#### Option 3: LoadBalancer

Change service type in [service.yaml](service.yaml):
```yaml
spec:
  type: LoadBalancer
```

Then get the external IP:
```bash
kubectl get service ai-support-service
```

## Testing the API

### Health Check

```bash
kubectl port-forward svc/ai-support-service 8080:80
curl http://localhost:8080/health
```

### Ask a Question

```bash
curl -X POST http://localhost:8080/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I reset my password?"}'
```

## Monitoring

### View Logs

```bash
# All pods
kubectl logs -l app=ai-support-service --tail=100 -f

# Specific pod
kubectl logs <pod-name> -f

# Previous container logs (if pod crashed)
kubectl logs <pod-name> --previous
```

### Pod Status

```bash
# Get pods
kubectl get pods -l app=ai-support-service

# Describe pod
kubectl describe pod <pod-name>

# Get events
kubectl get events --sort-by='.lastTimestamp'
```

### Metrics

```bash
# Pod metrics (requires metrics-server)
kubectl top pods -l app=ai-support-service

# Node metrics
kubectl top nodes
```

## Troubleshooting

### Pod not starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>

# Check events
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Health checks failing

```bash
# Check if service is responding
kubectl exec -it <pod-name> -- curl http://localhost:8000/health

# Adjust probe timings in deployment.yaml if needed
```

### HPA not scaling

```bash
# Ensure metrics-server is installed
kubectl get deployment metrics-server -n kube-system

# Check HPA status
kubectl describe hpa ai-support-service

# Generate load to test scaling
kubectl run -it --rm load-generator --image=busybox --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://ai-support-service/health; done"
```

## Updating the Deployment

### Update image

```bash
# Update image tag
kubectl set image deployment/ai-support-service ai-support-service=ai-support-service:v2

# Or edit deployment
kubectl edit deployment ai-support-service

# Or apply updated manifest
kubectl apply -f deployment.yaml
```

### Rollback

```bash
# View rollout history
kubectl rollout history deployment/ai-support-service

# Rollback to previous version
kubectl rollout undo deployment/ai-support-service

# Rollback to specific revision
kubectl rollout undo deployment/ai-support-service --to-revision=2
```

## Clean Up

```bash
# Delete all resources
kubectl delete -f .

# Or delete individually
kubectl delete deployment ai-support-service
kubectl delete service ai-support-service
kubectl delete hpa ai-support-service
kubectl delete secret ai-support-service-secrets
```

## Production Considerations

### 1. Resource Limits
- Monitor actual resource usage and adjust limits accordingly
- Consider using Vertical Pod Autoscaler (VPA) for optimization

### 2. Security
- Store secrets in a secure secret management system (e.g., HashiCorp Vault, AWS Secrets Manager)
- Use RBAC to restrict access to secrets
- Enable Pod Security Policies or Pod Security Standards
- Run containers as non-root user (already configured in Dockerfile)

### 3. High Availability
- Use pod anti-affinity to spread pods across nodes
- Set up PodDisruptionBudget to ensure minimum availability during updates
- Consider multi-zone deployment

### 4. Monitoring & Logging
- Integrate with Prometheus for metrics
- Set up centralized logging (ELK, Loki, etc.)
- Configure alerts for critical events

### 5. Network Policies
- Implement network policies to restrict pod-to-pod communication
- Limit ingress/egress traffic

### 6. Backup
- Back up persistent data if you add persistent volumes
- Document recovery procedures

## Example: Pod Anti-Affinity

Add to deployment.yaml:

```yaml
spec:
  template:
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - ai-support-service
              topologyKey: kubernetes.io/hostname
```

## Example: PodDisruptionBudget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ai-support-service-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: ai-support-service
```

## Support

For issues or questions:
- Check logs: `kubectl logs -l app=ai-support-service`
- Review events: `kubectl get events`
- Consult the main [README.md](../README.md)
