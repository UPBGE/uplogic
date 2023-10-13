from bge import render
from bge.types import KX_GameObject as GameObject
from uplogic.nodes import ULActionNode, ULOutSocket
from uplogic.utils.objects import rotate_to
from uplogic.utils.objects import move_to


class ULMoveToWithNavmesh(ULActionNode):

    class MotionPath(object):
        def __init__(self):
            self.points: list = []
            self.cursor: int = 0
            self.destination = None

        def next_point(self):
            if self.cursor < len(self.points):
                return self.points[self.cursor]
            else:
                return None

        def destination_changed(self, new_destination):
            return self.destination != new_destination

        def advance(self):
            self.cursor += 1
            return self.cursor < len(self.points)

    def __init__(self):
        ULActionNode.__init__(self)
        self.condition: bool = None
        self.moving_object: GameObject = None
        self.rotating_object: GameObject = None
        self.navmesh_object: GameObject = None
        self.destination_point = None
        self.move_dynamic: bool = None
        self.linear_speed: float = None
        self.reach_threshold: float = None
        self.look_at: bool = None
        self.rot_axis: int = None
        self.front_axis: int = None
        self.rot_speed: float = None
        self.visualize: bool = None
        self._motion_path = None
        self.done: bool = False
        self.finished: bool = False
        self.OUT = ULOutSocket(self, self.get_done)
        self.FINISHED = ULOutSocket(self, self.get_finished)
        self.POINT = ULOutSocket(self, self.get_point)

    def get_done(self):
        return self.done

    def get_finished(self):
        return self.finished

    def get_point(self):
        return self._motion_path.next_point()

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        moving_object: GameObject = self.get_input(self.moving_object)
        rotating_object: GameObject = self.get_input(self.rotating_object)
        navmesh_object: GameObject = self.get_input(self.navmesh_object)
        destination_point = self.get_input(self.destination_point)
        move_dynamic: bool = self.get_input(self.move_dynamic)
        linear_speed: float = self.get_input(self.linear_speed)
        reach_threshold: float = self.get_input(self.reach_threshold)
        look_at: bool = self.get_input(self.look_at)
        rot_axis: int = self.get_input(self.rot_axis)
        front_axis: int = self.get_input(self.front_axis)
        rot_speed: float = self.get_input(self.rot_speed)
        visualize: bool = self.get_input(self.visualize)
        self.finished = False
        if (
            (self._motion_path is None) or
            (self._motion_path.destination_changed(destination_point))
        ):
            points = navmesh_object.findPath(
                moving_object.worldPosition,
                destination_point
            )
            motion_path = ULMoveToWithNavmesh.MotionPath()
            motion_path.points = points[1:]
            motion_path.destination = destination_point
            self._motion_path = motion_path
        next_point = self._motion_path.next_point()
        if visualize:
            points = [moving_object.worldPosition.copy()]
            points.extend(self._motion_path.points[self._motion_path.cursor:])
            points.append(self._motion_path.destination)
            for i, p in enumerate(points):
                if i < len(points) - 1:
                    render.drawLine(
                        p, points[i + 1], [1, 0, 0, 1]
                    )
        if next_point:
            tpf = self.network.time_per_frame
            if look_at and (rotating_object is not None):
                rotate_to(
                    rotating_object,
                    next_point,
                    rot_axis,
                    front_axis,
                    rot_speed
                )
            ths = reach_threshold  # if next_point == self._motion_path.destination else .1  # noqa
            reached = move_to(
                moving_object,
                next_point,
                linear_speed,
                tpf,
                move_dynamic,
                ths
            )
            if reached:
                has_more = self._motion_path.advance()
                if not has_more:
                    self.finished = True
            self.done = True