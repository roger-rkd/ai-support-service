# Deploy AI Support Service to Kubernetes
# Run this script after setting up your Kubernetes cluster

param(
    [switch]$Watch,
    [switch]$Logs
)

Write-Host "Deploying AI Support Service to Kubernetes..." -ForegroundColor Green

# Check if kubectl is configured
Write-Host "`nChecking Kubernetes cluster connection..." -ForegroundColor Yellow
$clusterInfo = kubectl cluster-info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Cannot connect to Kubernetes cluster!" -ForegroundColor Red
    Write-Host "Please ensure your cluster is running:" -ForegroundColor Yellow
    Write-Host "  - Docker Desktop: Enable Kubernetes in Settings" -ForegroundColor White
    Write-Host "  - Kind: Run .\setup-kind.ps1" -ForegroundColor White
    exit 1
}
Write-Host "Connected to cluster successfully!" -ForegroundColor Green

# Load Docker image to Kind if using Kind
$currentContext = kubectl config current-context
if ($currentContext -like "*kind*") {
    Write-Host "`nLoading Docker image to Kind cluster..." -ForegroundColor Yellow
    kind load docker-image ai-support-service:latest --name ai-support
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: Failed to load image. Make sure the image is built:" -ForegroundColor Yellow
        Write-Host "  docker build -t ai-support-service:latest ." -ForegroundColor White
    } else {
        Write-Host "Image loaded successfully!" -ForegroundColor Green
    }
}

# Deploy manifests
Write-Host "`nDeploying Kubernetes manifests..." -ForegroundColor Yellow

Write-Host "  - Creating secret..." -ForegroundColor Cyan
kubectl apply -f k8s/secret.yaml
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to create secret!" -ForegroundColor Red
    exit 1
}

Write-Host "  - Creating deployment..." -ForegroundColor Cyan
kubectl apply -f k8s/deployment.yaml

Write-Host "  - Creating service..." -ForegroundColor Cyan
kubectl apply -f k8s/service.yaml

Write-Host "  - Creating HPA..." -ForegroundColor Cyan
kubectl apply -f k8s/hpa.yaml

Write-Host "`nDeployment complete!" -ForegroundColor Green

# Wait for rollout
Write-Host "`nWaiting for deployment to be ready..." -ForegroundColor Yellow
kubectl rollout status deployment/ai-support-service --timeout=5m

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment is ready!" -ForegroundColor Green

    # Show status
    Write-Host "`n=== Deployment Status ===" -ForegroundColor Cyan
    kubectl get pods,svc,hpa -l app=ai-support-service

    Write-Host "`n=== Access the Service ===" -ForegroundColor Cyan
    Write-Host "Run the following command in a new terminal to access the service:" -ForegroundColor Yellow
    Write-Host "  kubectl port-forward svc/ai-support-service 8080:80" -ForegroundColor White
    Write-Host "`nThen test it:" -ForegroundColor Yellow
    Write-Host "  curl http://localhost:8080/health" -ForegroundColor White
    Write-Host "  curl -X POST http://localhost:8080/ask -H 'Content-Type: application/json' -d '{\"question\":\"How do I reset my password?\"}'" -ForegroundColor White

    if ($Logs) {
        Write-Host "`nShowing logs (Ctrl+C to stop)..." -ForegroundColor Yellow
        kubectl logs -l app=ai-support-service --tail=50 -f
    } elseif ($Watch) {
        Write-Host "`nWatching pods (Ctrl+C to stop)..." -ForegroundColor Yellow
        kubectl get pods -l app=ai-support-service --watch
    }
} else {
    Write-Host "Deployment failed or timed out!" -ForegroundColor Red
    Write-Host "Check logs with: kubectl logs -l app=ai-support-service" -ForegroundColor Yellow
    exit 1
}
