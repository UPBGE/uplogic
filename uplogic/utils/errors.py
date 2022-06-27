class NoXRSessionError(Exception):
    """No XR Session found."""
    def __init__(self, message="No active XR Session found!"):
        self.message = message
        super().__init__(self.message)


class PassIndexOccupiedError(Exception):
    """2D Filter pass index occupied."""
    def __init__(self, message="2D Filter pass index occupied!"):
        self.message = message
        super().__init__(self.message)
