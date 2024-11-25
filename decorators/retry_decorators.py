import time
from functools import wraps


def retry_on_failure(max_retries: int = 3, delay: int = 1):
    """
    Decorator to retry a function on failure, with configurable retries and delay.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(f"Attempt {attempts} failed with error : {e}")
                    if attempts >= max_retries:
                        raise Exception(f"Max Attempts failed, Error: {e}")
                    time.sleep(delay)

        return wrapper

    return decorator
