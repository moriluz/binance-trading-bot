#!/bin/bash
set -e

# Configuration
NAMESPACE="trading-bot"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if the namespace exists
if ! kubectl get namespace ${NAMESPACE} &> /dev/null; then
    echo "Creating namespace: ${NAMESPACE}"
    kubectl create namespace ${NAMESPACE}
fi

# Apply Kubernetes manifests using kustomize
echo "Deploying application to Kubernetes..."
kubectl apply -k k8s/

echo "Waiting for deployment to be ready..."
kubectl -n ${NAMESPACE} rollout status deployment/trading-bot

echo "Deployment completed successfully!"
echo "You can access the API using the following command:"
echo "  kubectl -n ${NAMESPACE} port-forward svc/trading-bot 8000:8000"
echo "Then open http://localhost:8000 in your browser."
