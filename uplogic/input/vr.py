'''OpenXR / VR input classes for uplogic.

Wraps the Blender ``xr_session_state`` API to expose headset pose and
controller data as :class:`VRHeadset`, :class:`VRController`, and the
convenience aggregate :class:`VRCharacter`.

Requires an active OpenXR session; constructors raise
:class:`~uplogic.utils.errors.NoXRSessionError` when none is available.
'''
import bpy
from mathutils import Quaternion
from mathutils import Matrix
from mathutils import Vector
from bge import logic
from uplogic import console
from bge.types import KX_GameObject as GameObject
from uplogic.utils.errors import NoXRSessionError


def get_vr_headset_data() -> tuple[Vector, Matrix]:
    '''Return the current position and orientation of the active VR headset.

    :returns: Tuple of ``(position, orientation)`` where *position* is a
        :class:`mathutils.Vector` and *orientation* is a
        :class:`mathutils.Matrix`.
    :raises NoXRSessionError: When no OpenXR session is active.
    '''
    session = bpy.context.window_manager.xr_session_state
    if not session:
        raise NoXRSessionError
    return (Vector(session.viewer_pose_location), Quaternion(session.viewer_pose_rotation).to_matrix())


class VRController():
    '''Wrapper for a single VR controller, exposing grip and aim pose data and
    input state via read-only properties.

    :param idx: Controller index — ``0`` for the left hand, ``1`` for the right.
    :raises NoXRSessionError: When no OpenXR session is active.
    '''

    _deprecated = False

    def __init__(self, idx: int=0) -> None:
        if self._deprecated:
            console.warning('Warning: ULControllerVR class will be renamed to "VRController" in future releases!')
        self.idx = idx
        self.stick_threshold = 0.0
        self.session = bpy.context.window_manager.xr_session_state
        if not self.session:
            raise NoXRSessionError

    @property
    def position(self) -> Vector:
        '''World-space grip position of the controller (read-only).'''
        return Vector(self.session.controller_grip_location_get(bpy.context, self.idx))

    @position.setter
    def position(self, val):
        console.debug("Attribute 'position' of 'VRController' is read-only!")

    @property
    def orientation(self) -> Matrix:
        '''World-space grip orientation of the controller as a :class:`mathutils.Matrix` (read-only).'''
        return Quaternion(self.session.controller_grip_rotation_get(bpy.context, self.idx)).to_matrix()

    @orientation.setter
    def orientation(self, val):
        console.debug("Attribute 'orientation' of 'VRController' is read-only!")

    @property
    def position_aim(self) -> Vector:
        '''World-space position of the controller's aim ray origin (read-only).'''
        return Vector(self.session.controller_aim_location_get(bpy.context, self.idx))

    @position_aim.setter
    def position_aim(self, val):
        console.debug("Attribute 'position_aim' of 'VRController' is read-only!")

    @property
    def orientation_aim(self) -> Matrix:
        '''World-space orientation of the controller's aim ray as a :class:`mathutils.Matrix` (read-only).'''
        return Quaternion(self.session.controller_aim_rotation_get(bpy.context, self.idx)).to_matrix()

    @orientation_aim.setter
    def orientation_aim(self, val):
        console.debug("Attribute 'orientation_aim' of 'VRController' is read-only!")

    @property
    def aim(self) -> Vector:
        '''Normalised targeting direction vector from grip to aim pose (read-only).'''
        aim = self.position_aim - self.position
        return aim.normalized()

    @aim.setter
    def aim(self, val):
        console.debug("Attribute 'aim' of 'VRController' is read-only!")

    @property
    def trigger(self) -> float:
        '''Trigger press intensity in the range ``[0, 1]`` (read-only).'''
        return self.session.action_state_get(
            bpy.context,
            'blender_default',
            'teleport',
            f"/user/hand/{'left' if self.idx == 0 else 'right'}"
        )[0]

    @trigger.setter
    def trigger(self, val):
        console.debug("Attribute 'trigger' of 'VRController' is read-only!")

    @property
    def thumbstick(self) -> Vector:
        '''Thumbstick deflection as a :class:`mathutils.Vector` of ``(x, y)`` (read-only). Left controller uses fly-right/fly-forward actions; right uses fly-turnright/fly-up.'''
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
        console.debug("Attribute 'thumbstick' of 'VRController' is read-only!")


class ULControllerVR(VRController):
    '''[DEPRECATED] Use :class:`VRController` instead.'''
    _deprecated = True


class VRHeadset():
    '''Wrapper for the VR headset viewer pose.

    Exposes the headset's world-space :attr:`position` and :attr:`orientation`
    as read-only properties drawn from the active OpenXR session.

    :raises NoXRSessionError: When no OpenXR session is active.
    '''

    _deprecated = False

    def __init__(self) -> None:
        if self._deprecated:
            console.warning('Warning: ULHeadsetVR class will be renamed to "VRHeadset" in future releases!')
        self.session = bpy.context.window_manager.xr_session_state
        if not self.session:
            raise NoXRSessionError

    @property
    def position(self) -> Vector:
        '''World-space headset viewer position (read-only).'''
        return Vector(self.session.viewer_pose_location)

    @position.setter
    def position(self, val):
        console.debug("Attribute 'position' of 'ULHeadsetVR' is read-only!")

    @property
    def orientation(self) -> Matrix:
        '''World-space headset viewer orientation as a :class:`mathutils.Matrix` (read-only).'''
        return Quaternion(self.session.viewer_pose_rotation).to_matrix()

    @orientation.setter
    def orientation(self, val):
        console.debug("Attribute 'orientation' of 'ULHeadsetVR' is read-only!")

    def getAxisVect(self, vector):
        '''Transform *vector* by the headset's current orientation matrix.

        :param vector: Input :class:`mathutils.Vector` in headset-local space.
        :returns: The vector rotated into world space.
        '''
        return self.orientation @ vector


class ULHeadsetVRWrapper(VRHeadset):
    '''Internal :class:`VRHeadset` subclass that exposes ``worldPosition`` and
    ``worldOrientation`` attributes so the headset can be used as a listener
    object in :class:`~uplogic.audio.audiosystem.AudioSystem` calculations.

    Not intended for direct use.
    '''
    @property
    def worldPosition(self) -> Vector:
        '''World-space headset position (mirrors :attr:`~VRHeadset.position`, read-only).'''
        return Vector(self.session.viewer_pose_location)

    @worldPosition.setter
    def worldPosition(self, val):
        console.debug("Attribute 'worldPosition' of 'ULHeadsetVRWrapper' is read-only!")

    @property
    def worldOrientation(self) -> Matrix:
        '''World-space headset orientation matrix (mirrors :attr:`~VRHeadset.orientation`, read-only).'''
        return Quaternion(self.session.viewer_pose_rotation).to_matrix()

    @worldOrientation.setter
    def worldOrientation(self, val):
        console.debug("Attribute 'worldOrientation' of 'ULHeadsetVRWrapper' is read-only!")

    def rayCast(
        self,
        obj_to,
        obj_from,
        distance,
        xray
    ):
        '''Delegate a ray-cast to the scene's active camera.

        :param obj_to: Target point or object.
        :param obj_from: Origin point or object.
        :param distance: Maximum ray distance.
        :param xray: When ``True``, pass through objects.
        :returns: Ray-cast result from :meth:`~bge.types.KX_Camera.rayCast`.
        '''
        return logic.getCurrentScene().active_camera.rayCast(obj_to, obj_from, distance, xray=xray)


class ULHeadsetVR(VRHeadset):
    '''[DEPRECATED] Use :class:`VRHeadset` instead.'''
    _deprecated = True


class VRCharacter():
    '''Aggregate wrapper combining a :class:`VRHeadset` and two
    :class:`VRController` instances (left and right hand).

    Optionally synchronises :class:`~bge.types.KX_GameObject` scene objects
    with the controller aim poses each frame.

    :param left_hand_object: Optional game object to track the left controller.
    :param right_hand_object: Optional game object to track the right controller.
    :raises NoXRSessionError: When no OpenXR session is active.
    '''
    _deprecated = False

    def __init__(
        self,
        left_hand_object: GameObject = None,
        right_hand_object: GameObject = None
    ) -> None:
        if self._deprecated:
            console.warning('Warning: ULCharacterVR class will be renamed to "VRCharacter" in future releases!')
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
        '''Per-frame update: sync the hand objects' world position and orientation
        with their respective controller aim poses.

        Called automatically via the scene pre-draw list when at least one hand
        object was provided.
        '''
        if self.hand_left_object:
            self.hand_left_object.worldPosition = self.hand_left.position_aim
            self.hand_left_object.worldOrientation = self.hand_left.orientation_aim
        if self.hand_right_object:
            self.hand_right_object.worldPosition = self.hand_right.position_aim
            self.hand_right_object.worldOrientation = self.hand_right.orientation_aim

    @property
    def position(self) -> Vector:
        '''World-space navigation origin of the VR rig (read-only).'''
        return Vector(self.session.navigation_location)

    @position.setter
    def position(self, val):
        console.debug("Attribute 'position' of 'ULHeadsetVR' is read-only!")

    @property
    def orientation(self) -> Matrix:
        '''World-space navigation orientation of the VR rig as a :class:`mathutils.Matrix` (read-only).'''
        return Quaternion(self.session.navigation_rotation).to_matrix()

    @orientation.setter
    def orientation(self, val):
        console.debug("Attribute 'orientation' of 'ULHeadsetVR' is read-only!")

    @property
    def scale(self) -> float:
        '''Navigation scale of the VR rig (read-only).'''
        return self.session.navigation_scale

    @scale.setter
    def scale(self, val):
        console.debug("Attribute 'scale' of 'ULHeadsetVR' is read-only!")


class ULCharacterVR(VRCharacter):
    '''[DEPRECATED] Use :class:`VRCharacter` instead.'''
    _deprecated = True


from uplogic.utils import check_vr_session_status


VR_STATE = check_vr_session_status()
VR_AUDIO = getattr(bpy.data.scenes[logic.getCurrentScene().name], 'use_vr_audio_space', False)
VR_HEADSET = VRHeadset() if check_vr_session_status() else None
