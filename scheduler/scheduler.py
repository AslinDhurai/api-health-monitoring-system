import json
import boto3
import time
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REGION = "ap-south-1"
SQS_QUEUE_URL = "https://sqs.ap-south-1.amazonaws.com/217190816821/health-check-jobs"
API_BASE_URL = "http://api-health-alb-776977953.ap-south-1.elb.amazonaws.com"

sqs = boto3.client("sqs", region_name=REGION)

while True:
    try:
        response = requests.get(f"{API_BASE_URL}/endpoints")
        endpoints = response.json()

        for endpoint in endpoints.values():
            message = {
                "endpoint_id": endpoint["id"],
                "url": endpoint["config"]["url"],
                "timeout": endpoint["config"]["timeout_seconds"],
                "expected_status": endpoint["config"]["expected_status"]
            }

            sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps(message)
            )

            logger.info(
                f"Enqueued job for {endpoint['config']['url']}"
            )

        time.sleep(60)

    except Exception as e:
        logger.error(e)
        time.sleep(10)

