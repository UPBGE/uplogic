class NoXRSessionError(Exception):
    def __init__(self, message="No active XR Session found!"):
        self.message = message
        super().__init__(self.message)
