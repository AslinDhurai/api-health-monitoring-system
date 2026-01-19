from worker import check_health

endpoint = {
    "config": type("obj", (), {
        "url": "https://api.github.com",
        "timeout_seconds": 5,
        "expected_status": 200
    })
}

print(check_health(endpoint))
