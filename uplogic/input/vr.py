import bpy
from mathutils import Quaternion
from mathutils import Matrix
from mathutils import Vector
from bge import logic
from bge.types import KX_GameObject as GameObject
from uplogic.utils.errors import NoXRSessionError


def get_vr_headset_data() -> tuple[Vector, Matrix]:
    """Get the current position and orientation of connected VR headset.

    :returns: `tuple` of (position: `Vector`, orientation: `Matrix`)
    """
    session = bpy.context.window_manager.xr_session_state
    if not session:
        raise NoXRSessionError
    return (Vector(session.viewer_pose_location), Quaternion(session.viewer_pose_rotation).to_matrix())


class VRController():
    """Wrapper class for VR Controllers.

    This wrapper provides `position`, `position_aim`, `orientation`,
    `orientation_aim`, `trigger` and `thumbstick` attributes.

    :param `idx`: Controller index; 0 for left, 1 for right controller.
    """

    _deprecated = False

    def __init__(self, idx: int=0) -> None:
        if self._deprecated:
            print('Warning: ULControllerVR class will be renamed to "VRController" in future releases!')
        self.idx = idx
        self.stick_threshold = 0.0
        self.session = bpy.context.window_manager.xr_session_state
        if not self.session:
            raise NoXRSessionError

    @property
    def position(self) -> Vector:
        """The global position of the controller."""
        return Vector(self.session.controller_grip_location_get(bpy.context, self.idx))

    @position.setter
    def position(self, val):
        print("Attribute 'position' of 'ULControllerVR' is read-only!")

    @property
    def orientation(self) -> Matrix:
        """The global orientation of the controller."""
        return Quaternion(self.session.controller_grip_rotation_get(bpy.context, self.idx)).to_matrix()

    @orientation.setter
    def orientation(self, val):
        print("Attribute 'orientation' of 'ULControllerVR' is read-only!")

    @property
    def position_aim(self) -> Vector:
        """The global position of the tip of the controller."""
        return Vector(self.session.controller_aim_location_get(bpy.context, self.idx))

    @position_aim.setter
    def position_aim(self, val):
        print("Attribute 'position_aim' of 'ULControllerVR' is read-only!")

    @property
    def orientation_aim(self) -> Matrix:
        """The global orientation of the tip of the controller."""
        return Quaternion(self.session.controller_aim_rotation_get(bpy.context, self.idx)).to_matrix()

    @orientation_aim.setter
    def orientation_aim(self, val):
        print("Attribute 'orientation_aim' of 'ULControllerVR' is read-only!")

    @property
    def aim(self) -> Vector:
        """Targeting vector of the controller."""
        aim = self.position_aim - self.position
        return aim.normalized()

    @aim.setter
    def aim(self, val):
        print("Attribute 'aim' of 'ULControllerVR' is read-only!")

    @property
    def trigger(self) -> float:
        """The intensity with which the trigger on the controller is pressed."""
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
        """Stick values for the controller."""
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


class ULControllerVR(VRController):
    _deprecated = True


class VRHeadset():
    """Wrapper class for a VR Headset.

    This wrapper provides a `position` and an `orientation`
    attribute.
    """

    _deprecated = False

    def __init__(self) -> None:
        if self._deprecated:
            print('Warning: ULHeadsetVR class will be renamed to "VRHeadset" in future releases!')
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


class ULHeadsetVRWrapper(VRHeadset):
    """Wrapper class for a VR Headset to be used for audio calculations.

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


class ULHeadsetVR(VRHeadset):
    _deprecated = True


class VRCharacter():
    """Wrapper class for all VR Devices. This wrapper contains 2 `ULControllerVR` objects as well as one
    `ULHeadsetVR` object.

    Optionally, `KX_GameObjects` can be defined for both left and right controller. These objects will by
    automatically synched with their respective controller's position and orientation.
    """
    _deprecated = False

    def __init__(
        self,
        left_hand_object: GameObject = None,
        right_hand_object: GameObject = None
    ) -> None:
        if self._deprecated:
            print('Warning: ULCharacterVR class will be renamed to "VRCharacter" in future releases!')
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


class ULCharacterVR(VRCharacter):
    _deprecated = True
