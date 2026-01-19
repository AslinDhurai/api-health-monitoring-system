resource "aws_sqs_queue" "health_jobs" {
  name                      = "health-check-jobs"
  visibility_timeout_seconds = 60
}

resource "aws_sqs_queue" "health_dlq" {
  name = "health-check-dlq"
}
