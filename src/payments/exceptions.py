class IdempotencyKeyException(Exception):
    def __init__(self, message="Idempotency key already used with a different request payload"):
        self.message = message
