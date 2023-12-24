class DatabaseConnectionException(Exception):
    def __init__(self, message="Database connection error", details=None):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}: {self.details}" if self.details else self.message
