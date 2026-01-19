def notify(endpoint_id, old_state, new_state):
    print(
        f"[ALERT] Endpoint {endpoint_id} changed from {old_state} → {new_state}"
    )
