pipeline {
    agent any

    environment {
        // Path to your PEM key on YOUR LOCAL MAC
        // Jenkins needs read access to this file.
        // Update this path to where your key actually is.
        SSH_KEY_PATH = "/Users/anuragstark/Downloads/roi-platform-key.pem" 
        
        // AWS Region
        AWS_REGION = "us-east-1"
        
        // Terraform Directory
        TF_DIR = "infra"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Terraform Init & Apply') {
            steps {
                script {
                    dir(TF_DIR) {
                        // Ensure Terraform plugins are installed
                        sh 'terraform init'
                        
                        // Apply Infrastructure (EC2 + Security Groups)
                        // using -auto-approve to run without manual confirmation
                        sh 'terraform apply -auto-approve'
                        
                        // Capture the Public IP for the next stage
                        env.INSTANCE_IP = sh(script: 'terraform output -raw instance_public_ip', returnStdout: true).trim()
                        echo "Infrastructure Ready! Instance IP: ${env.INSTANCE_IP}"
                    }
                }
            }
        }

        stage('Wait for Instance SSH') {
            steps {
                script {
                    echo "Waiting for EC2 instance to be ready for SSH..."
                    sleep 60 // Wait 60 seconds for instance boot and SSH startup
                }
            }
        }

        stage('Deploy App to EC2') {
            steps {
                script {
                    def remoteCmd = """
                        # Stop existing container if running
                        sudo docker stop snake-game-app || true
                        sudo docker rm snake-game-app || true
                        
                        # Pull latest code (Simple approach: Clone/Pull in a temp dir or just build here)
                        # Here we will just build from a clean clone to ensure freshness
                        rm -rf snake-game-k8s-monitoring || true
                        git clone https://github.com/anuragstark/snake-game-k8s-monitoring.git
                        cd snake-game-k8s-monitoring
                        
                        # Build Docker Image
                        sudo docker build -t snake-game .
                        
                        # Run Container
                        sudo docker run -d --name snake-game-app -p 5000:5000 --restart always snake-game
                    """
                    
                    // Execute SSH command using the local key
                    // StrictHostKeyChecking=no prevents asking to add fingerprint to known_hosts
                    sh "ssh -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} ubuntu@${env.INSTANCE_IP} '${remoteCmd}'"
                }
            }
        }
    }

    post {
        success {
            echo "Deployment Completed Successfully!"
            echo "Access your app here: http://${env.INSTANCE_IP}:5000"
        }
        failure {
            echo "Deployment Failed. Check logs."
        }
    }
}
