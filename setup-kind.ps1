# Setup Kind (Kubernetes in Docker) for local development
# Run this script in PowerShell as Administrator

Write-Host "Installing Kind (Kubernetes in Docker)..." -ForegroundColor Green

# Download Kind for Windows
$kindVersion = "v0.20.0"
$kindUrl = "https://kind.sigs.k8s.io/dl/$kindVersion/kind-windows-amd64"
$kindPath = "$env:USERPROFILE\bin\kind.exe"

# Create bin directory if it doesn't exist
New-Item -Path "$env:USERPROFILE\bin" -ItemType Directory -Force | Out-Null

# Download Kind
Write-Host "Downloading Kind $kindVersion..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $kindUrl -OutFile $kindPath

# Add to PATH if not already there
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$env:USERPROFILE\bin*") {
    Write-Host "Adding Kind to PATH..." -ForegroundColor Yellow
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$env:USERPROFILE\bin", "User")
    $env:Path = "$env:Path;$env:USERPROFILE\bin"
}

Write-Host "Kind installed successfully!" -ForegroundColor Green
Write-Host "`nCreating Kind cluster..." -ForegroundColor Green

# Create Kind cluster with custom configuration
$kindConfig = @"
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30080
    hostPort: 8080
    protocol: TCP
"@

$kindConfig | Out-File -FilePath "$env:TEMP\kind-config.yaml" -Encoding utf8

# Create cluster
& "$kindPath" create cluster --name ai-support --config "$env:TEMP\kind-config.yaml"

Write-Host "`nKind cluster 'ai-support' created successfully!" -ForegroundColor Green
Write-Host "You can now deploy your application with:" -ForegroundColor Cyan
Write-Host "  kubectl apply -f k8s/" -ForegroundColor White

# Clean up
Remove-Item "$env:TEMP\kind-config.yaml" -ErrorAction SilentlyContinue

Write-Host "`nUseful commands:" -ForegroundColor Yellow
Write-Host "  kind get clusters" -ForegroundColor White
Write-Host "  kubectl cluster-info" -ForegroundColor White
Write-Host "  kind delete cluster --name ai-support" -ForegroundColor White
