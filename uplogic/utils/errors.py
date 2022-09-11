class NoXRSessionError(Exception):
    """No XR Session found."""
    def __init__(self, message="No active XR Session found!"):
        self.message = message
        super().__init__(self.message)


class PassIndexOccupiedError(Exception):
    """2D Filter pass index already in-use."""
    def __init__(self, idx=0):
        self.message = f"2D Filter pass index {idx} already in-use!"
        super().__init__(self.message)


class LogicControllerNotSupportedError(Exception):
    """Expression/Python not supported for controller."""
    def __init__(self, message="Expression/Python not supported for controller!"):
        self.message = message
        super().__init__(self.message)


class TypeMismatchError(Exception):
    """Type mismatch."""
    def __init__(self, msg='Type Mismatch!'):
        super().__init__(msg)