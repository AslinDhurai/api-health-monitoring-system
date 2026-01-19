resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/ecs/api-health-api"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "worker_logs" {
  name              = "/ecs/api-health-worker"
  retention_in_days = 7
}

