from celery import shared_task
from time import sleep

@shared_task
def add(x, y):
    print(f"Task started: adding {x} + {y}")
    sleep(2)  # Simulate work
    result = x + y
    print(f"Task result: {result}")
    return result

# Optional testing code (only runs when executed directly)
if __name__ == "__main__":
    from .celery import app  # Import your Celery app
    result = add.apply_async((2, 3), countdown=5)
    print("Waiting for result...")
    print("Result:", result.get(timeout=30))
