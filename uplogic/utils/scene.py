from bge import logic
import bpy


def set_scene(scene: str or bpy.types.Scene) -> None:
    """Set a scene.
    """
    if isinstance(scene, str):
        scene = bpy.data.scenes.get(scene)
    if not scene:
        return
    obj = bpy.data.objects.new('Empty', None)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.logic.sensor_add(
        type='ALWAYS',
        name='Always',
        object=obj.name
    )
    bpy.ops.logic.controller_add(
        type='LOGIC_AND',
        name='And',
        object=obj.name
    )
    bpy.ops.logic.actuator_add(
        type='SCENE',
        name='Set Scene',
        object=obj.name
    )
    always_brick = obj.game.sensors['Always']
    and_brick = obj.game.controllers['And']
    scene_brick = obj.game.actuators['Set Scene']
    scene_brick.mode = 'SET'
    scene_brick.scene = scene

    always_brick.link(and_brick)
    and_brick.link(actuator=scene_brick)

    logic.getCurrentScene().convertBlenderObject(obj)