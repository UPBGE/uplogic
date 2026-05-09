'''Custom exception types for the uplogic BGE utility library.

Provides specialised exceptions for XR session errors, 2D filter pass
conflicts, unsupported logic controller types, and type mismatches.
'''


class NoXRSessionError(Exception):
    '''Raised when no active BGE XR session can be found.'''

    def __init__(self, message="No active XR Session found!"):
        '''Initialise with an optional custom message.

        :param message: Human-readable error description.
        '''
        self.message = message
        super().__init__(self.message)


class PassIndexOccupiedError(Exception):
    '''Raised when a 2D filter pass index is already in use.'''

    def __init__(self, idx=0):
        '''Initialise with the conflicting pass index.

        :param idx: The pass index that is already occupied.
        '''
        self.message = f"2D Filter pass index {idx} already in-use!"
        super().__init__(self.message)


class LogicControllerNotSupportedError(Exception):
    '''Raised when an unsupported BGE logic controller type is encountered.

    Expression and Python controller types are not supported in certain
    contexts; this exception signals that condition.
    '''

    def __init__(self, message="Expression/Python not supported for controller!"):
        '''Initialise with an optional custom message.

        :param message: Human-readable error description.
        '''
        self.message = message
        super().__init__(self.message)


class TypeMismatchError(Exception):
    '''Raised when a value does not match the expected type.'''

    def __init__(self, msg='Type Mismatch!'):
        '''Initialise with an optional custom message.

        :param msg: Human-readable description of the type mismatch.
        '''
        super().__init__(msg)
