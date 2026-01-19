import time
import json
import logging
import boto3
import requests
from botocore.exceptions import ClientError

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- CONFIG ----------------
REGION = "ap-south-1"
SQS_QUEUE_URL = "https://sqs.ap-south-1.amazonaws.com/217190816821/health-check-jobs"
STATE_TABLE_NAME = "health_state"
FAILURE_THRESHOLD = 3  # consecutive failures before marking UNHEALTHY

# ---------------- AWS CLIENTS ----------------
sqs = boto3.client("sqs", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)
state_table = dynamodb.Table(STATE_TABLE_NAME)

logger.info("Worker started and polling SQS...")

# ---------------- HEALTH CHECK FUNCTION ----------------
def check_health(endpoint):
    try:
        start = time.time()
        response = requests.get(
            endpoint["url"],
            timeout=endpoint["timeout"]
        )
        latency = time.time() - start

        healthy = response.status_code == endpoint["expected_status"]

        return {
            "healthy": healthy,
            "status_code": response.status_code,
            "latency_ms": int(latency * 1000)
        }

    except Exception as e:
        return {
            "healthy": False,
            "error": str(e)
        }

# ---------------- ALERT FUNCTION ----------------
def send_alert(endpoint_id, old_state, new_state):
    logger.warning(
        f"[ALERT] Endpoint {endpoint_id} changed from {old_state} → {new_state}"
    )

# ---------------- STATE EVALUATION ----------------
def evaluate_state(prev_state, prev_fail_count, healthy):
    if healthy:
        if prev_state == "UNHEALTHY":
            return "RECOVERED", 0
        return "HEALTHY", 0

    # unhealthy result
    new_fail_count = prev_fail_count + 1
    if new_fail_count >= FAILURE_THRESHOLD:
        return "UNHEALTHY", new_fail_count

    return prev_state or "UNKNOWN", new_fail_count

# ---------------- STATE UPDATE FUNCTION ----------------
def update_health_state(endpoint_id, result):
    now = int(time.time())

    try:
        # Fetch previous state
        prev_item = state_table.get_item(
            Key={"endpoint_id": endpoint_id}
        ).get("Item")

        prev_state = prev_item["status"] if prev_item else "UNKNOWN"
        prev_fail_count = prev_item["fail_count"] if prev_item else 0

        # Evaluate new state
        new_state, new_fail_count = evaluate_state(
            prev_state,
            prev_fail_count,
            result["healthy"]
        )

        item = {
            "endpoint_id": endpoint_id,
            "status": new_state,
            "fail_count": new_fail_count,
            "last_checked": now
        }

        if "latency_ms" in result:
            item["latency_ms"] = result["latency_ms"]

        if "status_code" in result:
            item["status_code"] = result["status_code"]

        # Persist state
        state_table.put_item(Item=item)

        # Alert only on state change
        if prev_state != new_state:
            send_alert(endpoint_id, prev_state, new_state)

        logger.info(
            f"State for {endpoint_id}: {prev_state} → {new_state} "
            f"(fail_count={new_fail_count})"
        )

    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")

# ---------------- WORKER LOOP ----------------
while True:
    try:
        response = sqs.receive_message(
            QueueUrl=SQS_QUEUE_URL,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=20
        )

        if "Messages" not in response:
            logger.info("No jobs in queue, waiting...")
            time.sleep(5)
            continue

        message = response["Messages"][0]
        endpoint = json.loads(message["Body"])

        logger.info(f"Checking health for {endpoint['url']}")

        result = check_health(endpoint)

        logger.info(f"Health result: {result}")

        # Update state + detect transitions
        update_health_state(endpoint["endpoint_id"], result)

        # Delete message after successful processing
        sqs.delete_message(
            QueueUrl=SQS_QUEUE_URL,
            ReceiptHandle=message["ReceiptHandle"]
        )

    except Exception as e:
        logger.error(f"Worker error: {e}")
        time.sleep(5)
