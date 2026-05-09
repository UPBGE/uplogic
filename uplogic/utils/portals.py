'''Lightweight value-portal system for passing data between uplogic nodes.
'''
from bge import logic


class Portal:
    '''A value holder that delegates to a connected node.

    When a ``node`` is assigned, reading ``.value`` returns
    ``self.node.value``. When no node is connected (``self.node is None``),
    ``.value`` returns ``None``.
    '''

    def __init__(self) -> None:
        '''Initialise the portal with no connected node.'''
        self.node = None

    @property
    def value(self):
        '''The current value sourced from the connected node.

        :returns: ``self.node.value`` when a node is connected, ``None``
            otherwise.
        '''
        if self.node is not None:
            return self.node.value
        return None


class Portals:
    '''Class-level registry that maps keys to ``Portal`` instances.

    All portals are stored in the shared ``_portals`` dict so that any part
    of the codebase can retrieve the same portal for a given key without
    needing a direct reference.
    '''

    _portals = {}
    '''Shared dict mapping arbitrary keys to their ``Portal`` instances.'''

    @classmethod
    def get(cls, key):
        '''Return the portal for *key*, creating it if it does not exist.

        :param key: An arbitrary hashable key identifying the portal.
        :returns: The existing ``Portal`` for *key*, or a freshly created
            one if *key* was not yet registered.
        '''
        portal = cls._portals.get(key, None)
        if portal is None:
            portal = Portal()
            cls._portals[key] = portal
        return portal
