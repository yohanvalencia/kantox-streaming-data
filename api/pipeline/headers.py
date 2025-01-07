class HeadersBuilder:
    def __init__(self):
        self.headers = []

    def addCorrelationId(self, correlation_id: str):
        if correlation_id:
            self.headers.append(("X-Correlation-ID", correlation_id.encode("utf-8")))
        return self

    def addErrorMessage(self, error_message: str):
        if error_message:
            self.headers.append(("X-Error-Message", error_message.encode("utf-8")))
        return self

    def build(self):
        """Return the constructed headers."""
        return self.headers
