def evaluate_state(prev_state, healthy, fail_count, threshold):
    if healthy:
        return "HEALTHY", 0

    fail_count += 1
    if fail_count >= threshold:
        return "UNHEALTHY", fail_count

    return prev_state, fail_count
