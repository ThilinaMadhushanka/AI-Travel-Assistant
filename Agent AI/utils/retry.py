import random

def get_retry_delay(attempt, base_delay=5, max_delay=60):
    return min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
