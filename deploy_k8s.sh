#!/bin/bash
set -e

# Function to show usage
function show_usage {
    echo "Usage: ./deploy_k8s.sh [start|stop|restart]"
    echo "  start   : Build, load, and deploy (auto-starts Minikube)"
    echo "  stop    : Delete all kubernetes resources"
    echo "  restart : Stop and then start"
    exit 1
}

# Function to check and start Minikube
function check_minikube {
    echo "[INFO] Checking Minikube status..."
    if ! minikube status | grep -q "Running"; then
        echo "[WARN] Minikube is not running. Starting Minikube..."
        minikube start
        if [ $? -ne 0 ]; then
            echo "[ERROR] Failed to start Minikube."
            exit 1
        fi
        echo "[INFO] Minikube started successfully."
    else
        echo "[INFO] Minikube is running."
    fi

    # Enable addons
    echo "[INFO] Ensuring addons are enabled..."
    minikube addons enable ingress
    minikube addons enable dashboard
}

# Function to start the application
function start {
    check_minikube

    echo "[INFO] Building Docker image..."
    eval $(minikube docker-env) # Use Minikube's Docker daemon to avoid loading
    docker build -t snake-game:latest .
    if [ $? -ne 0 ]; then
        echo "[ERROR] Docker build failed"
        exit 1
    fi

    # With minikube docker-env, 'minikube image load' is often not needed, 
    # but we keep it for safety if eval failed or driver differs.
    # However, 'eval $(minikube docker-env)' is the most robust way for local images.
    # We will use the load command as fallback or explicitly if not using docker-env.
    # Actually, let's stick to the previous 'load' method to be consistent with previous success.
    # Reset docker env to avoid confusion if script exits
    eval $(minikube docker-env -u)

    echo "[INFO] Loading image into Minikube..."
    minikube image load snake-game:latest

    echo "[INFO] Applying Kubernetes manifests..."
    kubectl apply -f k8s/deploy.yaml

    echo "[INFO] Waiting for rollout to complete..."
    kubectl rollout status deployment/snake-game

    echo "[INFO] Deployment complete."
    
    echo "=================================================="
    echo "                 ACCESS INSTRUCTIONS              "
    echo "=================================================="
    echo "1. App URL (Direct):"
    echo "   Run this command to get a temporary direct URL:"
    echo "   minikube service snake-game-service --url"
    
    echo ""
    echo "2. App URL (Permanent - Requires Tunnel):"
    echo "   http://snake-game.local"
    
    echo ""
    echo "3. Kubernetes Dashboard:"
    echo "   Run this command in a new terminal:"
    echo "   minikube dashboard"
    echo "=================================================="
}

# Function to stop the application
function stop {
    echo "[INFO] Deleting Kubernetes resources..."
    kubectl delete -f k8s/deploy.yaml --ignore-not-found
    echo "[INFO] Resources deleted."
}

# Check arguments
if [ "$#" -ne 1 ]; then
    show_usage
fi

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        start
        ;;
    *)
        show_usage
        ;;
esac
