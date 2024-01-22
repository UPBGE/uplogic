from mathutils import Vector
from uplogic.nodes import ULActionNode
from uplogic.utils.visualize import draw_line, draw_path, draw_box, draw_cube, draw_mesh, draw_arrow
from uplogic.nodes import ULOutSocket


class DrawNode(ULActionNode):
    def __init__(self):
        ULActionNode.__init__(self)
        self.condition = False
        self.color = (1, 1, 1, 1)
        self.origin = Vector((0, 0, 0))
        self.target = Vector((0, 0, 0))
        self.points = []
        self.length = 1.0
        self.width = 1.0
        self.height = 1.0
        self.object = None
        self.use_volume_origin = False
        self.done = False
        self.OUT = self.add_output(self.get_out)
        self.mode = 0
        self.modes = [
            self.draw_line,
            self.draw_arrow,
            self.draw_path,
            self.draw_cube,
            self.draw_box,
            self.draw_mesh
        ]

    def get_out(self):
        return self.done

    def draw_line(self):
        draw_line(
            self.get_input(self.origin),
            self.get_input(self.target),
            self.get_input(self.color)
        )

    def draw_arrow(self):
        draw_arrow(
            self.get_input(self.origin),
            self.get_input(self.target),
            self.get_input(self.color)
        )

    def draw_path(self):
        draw_path(
            self.get_input(self.points),
            self.get_input(self.color)
        )

    def draw_cube(self):
        draw_cube(
            self.get_input(self.origin),
            self.get_input(self.width),
            self.get_input(self.color),
            self.use_volume_origin
        )

    def draw_box(self):
        draw_box(
            self.get_input(self.origin),
            self.get_input(self.width),
            self.get_input(self.length),
            self.get_input(self.height),
            self.get_input(self.color),
            self.use_volume_origin
        )

    def draw_mesh(self):
        draw_mesh(
            self.get_input(self.object),
            self.get_input(self.color)
        )

    def evaluate(self):
        self.done = False
        if not self.get_input(self.condition):
            return
        self.modes[self.mode]()
        self.done = True
