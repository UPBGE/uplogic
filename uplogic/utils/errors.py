class NoXRSessionError(Exception):
    """No XR Session found."""
    def __init__(self, message="No active XR Session found!"):
        self.message = message
        super().__init__(self.message)
