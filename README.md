# 🐍 Snake Game - K8s Monitoring

A classic Snake Game built with **Python Flask**, containerized with **Docker**, and deployed on **Kubernetes (Minikube)** with Ingress support.

##  Features

*   **Classic Game Logic**: Built with JavaScript and HTML5 Canvas.
*   **Backend**: Python Flask app for serving the game and API endpoints.
*   **Database**: SQLite to store high scores (persisted via Kubernetes PVC).
*   **Kubernetes Deployment**:
    *   **High Availability**: 2 Replicas.
    *   **Persistence**: Data survives pod restarts and deployments.
    *   **Ingress**: Custom domain support (`http://snake-game.local`).

##  Prerequisites

*   [Docker](https://www.docker.com/)
*   [Minikube](https://minikube.sigs.k8s.io/docs/start/)
*   [Kubectl](https://kubernetes.io/docs/tasks/tools/)

##  Quick Start

We provide a robust automation script valid for **macOS** and **Linux**.

### 1. Start / Deploy
This command checks Minikube status, enables addons, builds the image, and deploys everything.
```bash
./deploy_k8s.sh start
```

### 2. Access the Game
*   **Direct URL**: The script will output a command like `minikube service ... --url`. Run that to get a temporary URL.
*   **Permanent URL**: [http://snake-game.local](http://snake-game.local)
    *   *Requires `sudo minikube tunnel` running in a separate terminal.*
    *   *Requires `127.0.0.1 snake-game.local` in your `/etc/hosts`.*

### 3. Stop / Destroy
To delete all Kubernetes resources (Deployment, Service, Ingress, PVC):
```bash
./deploy_k8s.sh stop
```

### 4. Restart (Re-deploy)
```bash
./deploy_k8s.sh restart
```

##  Architecture via Kubernetes

The project uses a consolidated manifest `k8s/deploy.yaml` which creates:
1.  **ConfigMap & Secret**: For environment variables (`FLASK_ENV`, `DATABASE_URL`, `SECRET_KEY`).
2.  **PersistentVolumeClaim (PVC)**: `1Gi` storage for `snake_game.db` persistence.
3.  **Deployment**: 2 Pods running `snake-game:latest`.
4.  **Service**: NodePort service exposing port 5000.
5.  **Ingress**: Nginx ingress controller routing `snake-game.local` to the service.

##  Deployment & CI/CD (AWS & Jenkins)

We support a full CI/CD pipeline employing **Local Jenkins**, **Terraform**, and **AWS EC2**.

### Infrastructure (Terraform)
Located in `infra/`, our Terraform code provisions:
*   **AWS EC2 Instance** (Ubuntu 22.04 with Docker pre-installed).
*   **Security Groups** allowing access to ports 22, 80, 443, and 5000.

### Automated Pipeline (Jenkins)
The `Jenkinsfile` defines a pipeline that:
1.  **Provisions Infra**: Runs `terraform apply` to create/update the EC2 instance.
2.  **Deploys Application**: SSHs into the instance, pulls the latest code, builds the Docker image, and runs the container.

### Setup Guide
For a detailed step-by-step guide on setting up this pipeline on your local machine using **Ngrok** and **GitHub Webhooks**, please refer to:
👉 [**JENKINS_LOCAL_GUIDE.md**](./JENKINS_LOCAL_GUIDE.md)

##  Project Structure

```
.
├── app.py                 # Flask Application
├── Dockerfile             # Container definition
├── deploy_k8s.sh          # Automation Script
├── k8s/
│   └── deploy.yaml        # All-in-one Kubernetes Manifest
├── requirements.txt       # Python dependencies
└── ...
```

##  License
This project is open source.
