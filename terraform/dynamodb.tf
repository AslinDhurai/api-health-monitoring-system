resource "aws_dynamodb_table" "endpoints" {
  name         = "health_endpoints"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "endpoint_id"

  attribute {
    name = "endpoint_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "health_state" {
  name         = "health_state"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "endpoint_id"

  attribute {
    name = "endpoint_id"
    type = "S"
  }
}
