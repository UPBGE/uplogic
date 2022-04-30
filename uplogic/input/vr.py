import bpy
from mathutils import Quaternion
from mathutils import Matrix
from mathutils import Vector
from bge import logic
from bge.types import KX_GameObject as GameObject
from uplogic.utils.errors import NoXRSessionError


def get_vr_headset_data() -> tuple[Vector, Matrix]:
    """Get the current position and orientation of connected VR headset.
    :returns: `tuple` of (`Vector`, `Matrix`)
    """
    session = bpy.context.window_manager.xr_session_state
    if not session:
        raise NoXRSessionError
    return (Vector(session.viewer_pose_location), Quaternion(session.viewer_pose_rotation).to_matrix())


class ULControllerVR():
    """Wrapper class for VR Controllers.\n
    This wrapper provides `position`, `position_aim`, `orientation`,
    `orientation_aim`, `trigger` and `thumbstick` attributes.
    """

    def __init__(self, idx: int=0) -> None:
        self.idx = idx
        self.stick_threshold = 0.0
        self.session = bpy.context.window_manager.xr_session_state
        if not self.session:
            raise NoXRSessionError

    @property
    def position(self) -> Vector:
        return Vector(self.session.controller_grip_location_get(bpy.context, self.idx))

    @position.setter
    def position(self, val):
        print("Attribute 'position' of 'ULControllerVR' is read-only!")

    @property
    def orientation(self) -> Matrix:
        return Quaternion(self.session.controller_grip_rotation_get(bpy.context, self.idx)).to_matrix()

    @orientation.setter
    def orientation(self, val):
        print("Attribute 'orientation' of 'ULControllerVR' is read-only!")

    @property
    def position_aim(self) -> Vector:
        return Vector(self.session.controller_aim_location_get(bpy.context, self.idx))

    @position_aim.setter
    def position_aim(self, val):
        print("Attribute 'position_aim' of 'ULControllerVR' is read-only!")

    @property
    def orientation_aim(self) -> Matrix:
        return Quaternion(self.session.controller_aim_rotation_get(bpy.context, self.idx)).to_matrix()

    @orientation_aim.setter
    def orientation_aim(self, val):
        print("Attribute 'orientation_aim' of 'ULControllerVR' is read-only!")

    @property
    def aim(self) -> Matrix:
        aim = self.position_aim - self.position
        aim.normalize()
        return aim

    @aim.setter
    def aim(self, val):
        print("Attribute 'aim' of 'ULControllerVR' is read-only!")

    @property
    def trigger(self) -> float:
        return self.session.action_state_get(
            bpy.context,
            'blender_default',
            'teleport',
            f"/user/hand/{'left' if self.idx == 0 else 'right'}"
        )[0]

    @trigger.setter
    def trigger(self, val):
        print("Attribute 'trigger' of 'ULControllerVR' is read-only!")

    @property
    def thumbstick(self) -> Vector:
        if self.idx == 0:
            x = self.session.action_state_get(
                bpy.context,
                'blender_default',
                'fly_right',
                '/user/hand/left'
            )[0]
            y = self.session.action_state_get(
                bpy.context,
                'blender_default',
                'fly_forward',
                '/user/hand/left'
            )[0]
            return Vector((x, y))
        else:
            x = self.session.action_state_get(
                bpy.context,
                'blender_default',
                'fly_turnright',
                '/user/hand/right'
            )[0]
            y = self.session.action_state_get(
                bpy.context,
                'blender_default',
                'fly_up',
                '/user/hand/right'
            )[0]
            return Vector((x, y))

    @thumbstick.setter
    def thumbstick(self, val):
        print("Attribute 'thumbstick' of 'ULControllerVR' is read-only!")


class ULHeadsetVR():
    """Wrapper class for a VR Headset.\n
    This wrapper provides a `position` and an `orientation`
    attribute.
    """
    def __init__(self) -> None:
        self.session = bpy.context.window_manager.xr_session_state
        if not self.session:
            raise NoXRSessionError

    @property
    def position(self) -> Vector:
        return Vector(self.session.viewer_pose_location)

    @position.setter
    def position(self, val):
        print("Attribute 'position' of 'ULHeadsetVR' is read-only!")

    @property
    def orientation(self) -> Matrix:
        return Quaternion(self.session.viewer_pose_rotation).to_matrix()

    @orientation.setter
    def orientation(self, val):
        print("Attribute 'orientation' of 'ULHeadsetVR' is read-only!")


class ULHeadsetVRWrapper(ULHeadsetVR):
    """Wrapper class for a VR Headset to be used for audio calculations.\n
    Not intended for manual use.
    """
    @property
    def worldPosition(self) -> Vector:
        return Vector(self.session.viewer_pose_location)

    @worldPosition.setter
    def worldPosition(self, val):
        print("Attribute 'worldPosition' of 'ULHeadsetVRWrapper' is read-only!")

    @property
    def worldOrientation(self) -> Matrix:
        return Quaternion(self.session.viewer_pose_rotation).to_matrix()

    @worldOrientation.setter
    def worldOrientation(self, val):
        print("Attribute 'worldOrientation' of 'ULHeadsetVRWrapper' is read-only!")
    
    def rayCast(
        self,
        obj_to,
        obj_from,
        distance,
        xray
    ):
        return logic.getCurrentScene().active_camera.rayCast(obj_to, obj_from, distance, xray=xray)


class ULCharacterVR():
    """Wrapper class for all VR Devices. This wrapper contains 2 `ULControllerVR` objects as well as one
    `ULHeadsetVR` object.\n
    Optionally, `KX_GameObjects` can be defined for both left and right controller. These objects will by
    automatically synched with their respective controller's position and orientation.\n
    This class provides a `position` an `orientation` and a `scale` attribute.
    """
    def __init__(
        self,
        left_hand_object: GameObject = None,
        right_hand_object: GameObject = None
    ) -> None:
        self.session = bpy.context.window_manager.xr_session_state
        if not self.session:
            raise NoXRSessionError
        self.hand_left = ULControllerVR(0)
        self.hand_right = ULControllerVR(1)
        self.head = ULHeadsetVR()
        self.hand_left_object = left_hand_object
        self.hand_right_object = right_hand_object
        if left_hand_object is not None or right_hand_object is not None:
            logic.getCurrentScene().pre_draw.append(self.update)
    
    def update(self):
        if self.hand_left_object:
            self.hand_left_object.worldPosition = self.hand_left.position_aim
            self.hand_left_object.worldOrientation = self.hand_left.orientation_aim
        if self.hand_right_object:
            self.hand_right_object.worldPosition = self.hand_right.position_aim
            self.hand_right_object.worldOrientation = self.hand_right.orientation_aim

    @property
    def position(self) -> Vector:
        return Vector(self.session.navigation_location)

    @position.setter
    def position(self, val):
        print("Attribute 'position' of 'ULHeadsetVR' is read-only!")

    @property
    def orientation(self) -> Matrix:
        return Quaternion(self.session.navigation_rotation).to_matrix()

    @orientation.setter
    def orientation(self, val):
        print("Attribute 'orientation' of 'ULHeadsetVR' is read-only!")

    @property
    def scale(self) -> float:
        return self.session.navigation_scale

    @scale.setter
    def scale(self, val):
        print("Attribute 'scale' of 'ULHeadsetVR' is read-only!")
