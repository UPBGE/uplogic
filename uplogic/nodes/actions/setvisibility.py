from uplogic.nodes import ULActionNode
from uplogic.utils import logic
from bpy.types import Collection
from bge.types import KX_GameObject
from bge.types import KX_Scene
import bpy


class ULSetVisibility(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.game_object = None
        self.visible: bool = None
        self.recursive: bool = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def evaluate(self):
        if not self.get_condition():
            return
        game_object: KX_GameObject = self.get_input(self.game_object)
        visible: bool = self.get_input(self.visible)
        recursive: bool = self.get_input(self.recursive)
        game_object.setVisible(visible, recursive)
        self._done = True


class ULSetCollectionVisibility(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = None
        self.collection = None
        self.visible: bool = None
        self.recursive: bool = None
        self.OUT = self.add_output(self.get_done)

    def get_done(self):
        return self._done

    def set_collection_visible(
        self,
        visible,
        recursive,
        scene: KX_Scene,
        collection:Collection
    ):
        for o in collection.objects:
            gameObject = scene.getGameObjectFromObject(o)
            if gameObject:
                gameObject.setVisible(visible, True)
        if recursive:
            if len(collection.children) <= 0:
                return
            for child in collection.children:
                self.set_collection_visible(visible, recursive, scene, child)

    def evaluate(self):
        if not self.get_condition():
            return
        collection: Collection = self.get_input(self.collection)
        visible: bool = self.get_input(self.visible)
        recursive: bool = self.get_input(self.recursive)
        scene = logic.getCurrentScene()
        self.set_collection_visible(visible, recursive, scene, collection)
        self._done = True
