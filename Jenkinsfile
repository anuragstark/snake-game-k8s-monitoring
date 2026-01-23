pipeline {
    agent any

    parameters {
        choice(name: 'ACTION', choices: ['APPLY', 'DESTROY'], description: 'Choose infrastructure action')
    }

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

        stage('Terraform Apply') {
            when {
                expression { params.ACTION == 'APPLY' }
            }
            steps {
                script {
                    dir(TF_DIR) {
                        sh 'terraform init'
                        sh 'terraform apply -auto-approve'
                        
                        // Capture IP only on Apply
                        env.INSTANCE_IP = sh(script: 'terraform output -raw instance_public_ip', returnStdout: true).trim()
                        echo "Infrastructure Ready! Instance IP: ${env.INSTANCE_IP}"
                    }
                }
            }
        }

        stage('Wait for Instance SSH') {
            when {
                expression { params.ACTION == 'APPLY' }
            }
            steps {
                script {
                    echo "Waiting for EC2 instance to be ready for SSH..."
                    sleep 60 
                }
            }
        }

        stage('Deploy App to EC2') {
            when {
                expression { params.ACTION == 'APPLY' }
            }
            steps {
                script {
                    def remoteCmd = """
                        sudo docker stop snake-game-app || true
                        sudo docker rm snake-game-app || true
                        rm -rf snake-game-k8s-monitoring || true
                        git clone https://github.com/anuragstark/snake-game-k8s-monitoring.git
                        cd snake-game-k8s-monitoring
                        sudo docker build -t snake-game .
                        sudo docker run -d --name snake-game-app -p 5000:5000 --restart always snake-game
                    """
                    
                    sh "ssh -o StrictHostKeyChecking=no -i ${SSH_KEY_PATH} ubuntu@${env.INSTANCE_IP} '${remoteCmd}'"
                }
            }
        }

        stage('Terraform Destroy') {
            when {
                expression { params.ACTION == 'DESTROY' }
            }
            steps {
                script {
                    dir(TF_DIR) {
                        sh 'terraform init'
                        sh 'terraform destroy -auto-approve'
                        echo "Infrastructure Destroyed Successfully."
                    }
                }
            }
        }
    }

    post {
        success {
            echo "Pipeline [${params.ACTION}] Completed Successfully!"
            if (params.ACTION == 'APPLY') {
                echo "Access your app here: http://${env.INSTANCE_IP}:5000"
            }
        }
        failure {
            echo "Pipeline Failed. Check logs."
        }
    }
}
