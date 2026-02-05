#!/bin/bash
# Deploy AI Support Service to Kubernetes

set -e

WATCH=false
LOGS=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --watch) WATCH=true ;;
        --logs) LOGS=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "Deploying AI Support Service to Kubernetes..."

# Check if kubectl is configured
echo ""
echo "Checking Kubernetes cluster connection..."
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster!"
    echo "Please ensure your cluster is running:"
    echo "  - Docker Desktop: Enable Kubernetes in Settings"
    echo "  - Kind: Run ./setup-kind.sh"
    exit 1
fi
echo "Connected to cluster successfully!"

# Load Docker image to Kind if using Kind
CURRENT_CONTEXT=$(kubectl config current-context)
if [[ $CURRENT_CONTEXT == *"kind"* ]]; then
    echo ""
    echo "Loading Docker image to Kind cluster..."
    if kind load docker-image ai-support-service:latest --name ai-support; then
        echo "Image loaded successfully!"
    else
        echo "Warning: Failed to load image. Make sure the image is built:"
        echo "  docker build -t ai-support-service:latest ."
    fi
fi

# Deploy manifests
echo ""
echo "Deploying Kubernetes manifests..."

echo "  - Creating secret..."
kubectl apply -f k8s/secret.yaml

echo "  - Creating deployment..."
kubectl apply -f k8s/deployment.yaml

echo "  - Creating service..."
kubectl apply -f k8s/service.yaml

echo "  - Creating HPA..."
kubectl apply -f k8s/hpa.yaml

echo ""
echo "Deployment complete!"

# Wait for rollout
echo ""
echo "Waiting for deployment to be ready..."
if kubectl rollout status deployment/ai-support-service --timeout=5m; then
    echo "Deployment is ready!"

    # Show status
    echo ""
    echo "=== Deployment Status ==="
    kubectl get pods,svc,hpa -l app=ai-support-service

    echo ""
    echo "=== Access the Service ==="
    echo "Run the following command in a new terminal to access the service:"
    echo "  kubectl port-forward svc/ai-support-service 8080:80"
    echo ""
    echo "Then test it:"
    echo "  curl http://localhost:8080/health"
    echo "  curl -X POST http://localhost:8080/ask -H 'Content-Type: application/json' -d '{\"question\":\"How do I reset my password?\"}'"

    if [ "$LOGS" = true ]; then
        echo ""
        echo "Showing logs (Ctrl+C to stop)..."
        kubectl logs -l app=ai-support-service --tail=50 -f
    elif [ "$WATCH" = true ]; then
        echo ""
        echo "Watching pods (Ctrl+C to stop)..."
        kubectl get pods -l app=ai-support-service --watch
    fi
else
    echo "Deployment failed or timed out!"
    echo "Check logs with: kubectl logs -l app=ai-support-service"
    exit 1
fi
