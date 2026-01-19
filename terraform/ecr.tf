resource "aws_ecr_repository" "api" {
  name = "api-health-api"
}

resource "aws_ecr_repository" "worker" {
  name = "api-health-worker"
}

