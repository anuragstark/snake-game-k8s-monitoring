variable "aws_region" {
  description = "AWS Region to deploy resources"
  default     = "us-east-1"
}

variable "instance_type" {
  description = "EC2 Instance Type"
  default     = "t3.micro"
}

variable "key_name" {
  description = "Name of the existing SSH Key Pair"
  default     = "roi-platform-key"
}

variable "project_name" {
  description = "Name tag for the project resources"
  default     = "snake-game-app"
}
