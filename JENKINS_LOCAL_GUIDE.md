# Setup Guide: Local Jenkins to AWS Pipeline

This guide explains how to configure your **Local Jenkins** to receive GitHub pushes (via Ngrok) and deploy to AWS.

## 1. Prerequisites (On your Mac)

1.  **Install Jenkins**:
    ```bash
    brew install jenkins-lts
    brew services start jenkins-lts
    ```
    Access at `http://localhost:8080`.

2.  **Install Terraform**:
    ```bash
    brew install terraform
    ```

3.  **Install Ngrok**:
    ```bash
    brew install --cask ngrok
    ```

## 2. Prepare AWS Credentials

Jenkins needs permission to create EC2 instances.
1.  Go to **Jenkins Dashboard** -> **Manage Jenkins** -> **System**.
2.  Scroll to **Global properties** -> check **Environment variables**.
3.  Add the following variables (Use your actual AWS Keys):
    *   `AWS_ACCESS_KEY_ID`: `your_access_key`
    *   `AWS_SECRET_ACCESS_KEY`: `your_secret_key`
    *   `AWS_DEFAULT_REGION`: `us-east-1`

## 3. Configure SSH Key

1.  Your key is located at: `/Users/anuragstark/Downloads/roi-platform-key.pem`.
2.  Ensure Jenkins has read access to this file. Open a terminal and run:
    ```bash
    chmod 400 /Users/anuragstark/Downloads/roi-platform-key.pem
    ```
    *Note: If Jenkins still has permission issues, you might need to copy this key to a location Jenkins can definitely access (like `/Users/Shared/`) or adjust permissions, but try strictly 400 first.*

## 4. Expose Jenkins to GitHub (Ngrok)

1.  Open a terminal and run:
    ```bash
    ngrok http 8080
    ```
2.  Copy the `https` URL provided (e.g., `https://1234-56-78.ngrok-free.app`).
3.  Go to your **GitHub Repository** -> **Settings** -> **Webhooks** -> **Add webhook**.
    *   **Payload URL**: `<YOUR_NGROK_URL>/github-webhook/` (Don't forget the trailing slash!).
    *   **Content type**: `application/json`.
    *   **Events**: Just the `push` event.
    *   Click **Add webhook**.

## 5. Create Jenkins Job

1.  **New Item** -> Name: `snake-game-deploy` -> **Pipeline**.
2.  **Build Triggers**: Check `GitHub hook trigger for GITScm polling`.
3.  **Pipeline**:
    *   **Definition**: `Pipeline script from SCM`.
    *   **SCM**: `Git`.
    *   **Repository URL**: `https://github.com/anuragstark/snake-game-k8s-monitoring.git`.
    *   **Branch**: `*/main`.
    *   **Script Path**: `Jenkinsfile`.
4.  Click **Save**.

## 6. How it Works

1.  You push code to GitHub.
2.  GitHub sends a signal to Ngrok -> Local Jenkins.
3.  Jenkins initiates the job.
4.  **Stage 1**: Jenkins runs `terraform apply` locally.
    *   If infra exists, it updates it.
    *   If not, it creates it.
    *   It grabs the new IP address.
5.  **Stage 2**: Jenkins SSHs into that IP and deploys your code.
6.  **Done**: Jenkins prints the App URL.
8.  **Destroy**: To destroy the infrastructure, run `terraform destroy`.