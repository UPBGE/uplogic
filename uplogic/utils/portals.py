from bge import logic


class Portal:
    
    def __init__(self) -> None:
        self.node = None
    
    @property
    def value(self):
        if self.node is not None:
            return self.node.value
        return None


class Portals:

    _portals = {}

    @classmethod
    def get(cls, key):
        portal = cls._portals.get(key, None)
        if portal is None:
            portal = Portal()
            cls._portals[key] = portal
        return portal
