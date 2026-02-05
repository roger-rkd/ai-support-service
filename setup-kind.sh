#!/bin/bash
# Setup Kind (Kubernetes in Docker) for local development

echo "Installing Kind (Kubernetes in Docker)..."

# Install Kind
if ! command -v kind &> /dev/null; then
    echo "Downloading Kind..."
    curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
    chmod +x ./kind
    sudo mv ./kind /usr/local/bin/kind
    echo "Kind installed successfully!"
else
    echo "Kind is already installed"
fi

echo "Creating Kind cluster..."

# Create Kind cluster with custom configuration
cat <<EOF | kind create cluster --name ai-support --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30080
    hostPort: 8080
    protocol: TCP
EOF

echo "Kind cluster 'ai-support' created successfully!"
echo ""
echo "You can now deploy your application with:"
echo "  kubectl apply -f k8s/"
echo ""
echo "Useful commands:"
echo "  kind get clusters"
echo "  kubectl cluster-info"
echo "  kind delete cluster --name ai-support"
