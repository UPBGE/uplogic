from .widget import Widget
from .label import Label
from bge import logic
from bge import render
from mathutils import Vector
from math import degrees
from uplogic.utils import world_to_screen


class Compass(Widget):

    fragment_code = """
    // uniform sampler2D image;
    uniform vec4 primary_color;
    uniform vec4 secondary_color;
    uniform vec4 tertiary_color;
    uniform vec4 bg_color;
    uniform vec2 screen;
    uniform float camera_x;
    uniform float camera_y;
    uniform float bar_height;
    uniform float bar_width;
    uniform float elevation_position;
    uniform float fov;

    uniform int use_x;
    uniform int use_y;

    // Pixel Position from 0-1 in x, y
    in vec2 pxpos;

    out vec4 fragColor;

    void main()
    {
        float _bar_width = bar_width;

        float fov_factor = screen.y / screen.x;

        float x = ((.5 - pxpos[0]) * fov) + degrees(camera_x);
        float y = ((pxpos[1] - .5) * fov * fov_factor) + degrees(camera_y);

        if (abs(.5 - pxpos[0]) < _bar_width * 0.005 && abs(y - 90) < bar_height){
            fragColor = primary_color;
            return;
        }

        if (use_x == 1){
        
            for (int i = -360; i < 360; i = i + 90){
                float xangle = abs(x - i);
                float center_fac = 1 - (2 * abs(.5 - pxpos[0]));
                // fragColor = vec4(vec3(abs(y - 90) / 180), .9);
                // return;
                if (xangle < _bar_width && abs(y - 90) < bar_height){
                    vec4 col = primary_color;
                    col[3] *= center_fac;
                    fragColor = col;
                    return;
                }
            }
            for (int i = -360; i < 360; i = i + 45){
                //float xangle = abs(x + secondary_directions[i]);
                //if (xangle > 180) {
                //    xangle -= 180;
                //}
                
                float xangle = abs(x + i);
                float center_fac = 1 - (2 * abs(.5 - pxpos[0]));
                if (xangle < _bar_width * .75 && abs(y - 90) < bar_height * .5){
                    vec4 col = secondary_color;
                    col[3] *= center_fac;
                    fragColor = col;
                    return;
                }
            }
            for (int i = -360; i < 360; i = i + 5){
                //float xangle = abs(x + tertiary_directions[i]);
                //if (xangle > 180) {
                //    xangle -= 180;
                //}
                
                float xangle = abs(x + i);
                float center_fac = 1 - (2 * abs(.5 - pxpos[0]));
                if (xangle < _bar_width * .5 && abs(y - 90) < bar_height * .25){
                    vec4 col = tertiary_color;
                    col[3] *= center_fac;
                    fragColor = col;
                    return;
                }
            }
            if (abs(y - 90) < bar_height * 1.5){
                fragColor = bg_color;
                return;
            }
        }
        if (use_y == 1){
            for (int i = -180; i < 10; i = i + 5){
                float yangle = abs(y + i);
                float center_fac = 1 - (2 * abs(.5 - pxpos[1]));
                if (yangle < _bar_width * .5 && abs(pxpos[0] - elevation_position) < bar_height * .004){
                    vec4 col = tertiary_color;
                    col[3] *= center_fac;
                    fragColor = col;
                    return;
                }
            }
        }
        fragColor = vec4(0, 0, 0, 0);
    }
    """

    def __init__(
            self,
            primary_color=(1, 1, 1, 1),
            secondary_color=(1, 1, 1, .8),
            tertiary_color=(1, 1, 1, .5),
            bar_height=2,
            bar_width=.1,
            use_x=True,
            use_y=False,
            font='',
            font_size=20,
            bg_color=(0, 0, 0, 0),
            elevation_position=.5
        ):
        super().__init__(bg_color=bg_color)
        self.bar_height = bar_height
        self.bar_width = bar_width
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.tertiary_color = tertiary_color
        self.use_x = use_x
        self.use_y = use_y
        self.elevation_position = elevation_position
        self.angle_x_label = Label(
            font=font,
            font_size=font_size,
            shadow=True,
            relative={'pos': True},
            pos=(.5, .5),
            halign='center',
            font_color=primary_color
        )
        self.add_widget(self.angle_x_label)

    @property
    def _draw_size(self):
        return [
            render.getWindowWidth(),
            render.getWindowHeight()
        ]

    def set_uniforms(self):
        self.shader.uniform_float("screen", Vector((
            render.getWindowWidth(), render.getWindowHeight()
        )))
        cam = logic.getCurrentScene().active_camera
        view_dir = cam.getAxisVect((0, 0, -1))
        forward = view_dir.copy()
        forward.z = 0
        if not forward.xy.length > 0:
            return
        angle_x = -Vector((0, 1)).angle_signed(forward.xy.normalized())
        angle_y = view_dir.angle(Vector((0, 0, -1)))
        degrs = -round(degrees(angle_x))
        self.angle_x_label.text = f'{degrs if degrs >= 0 else 360 + degrs}°'

        self.angle_x_label.pos = world_to_screen(cam.worldPosition + forward, inv_y=False) - Vector((0, .25))

        # self.shader.uniform_sampler('image', self.canvas.image.texture)
        self.shader.uniform_float('camera_x', angle_x)
        self.shader.uniform_float('camera_y', angle_y)
        self.shader.uniform_float('primary_color', self.primary_color)
        self.shader.uniform_float('secondary_color', self.secondary_color)
        self.shader.uniform_float('tertiary_color', self.tertiary_color)
        self.shader.uniform_float('bg_color', self.bg_color)
        self.shader.uniform_float('fov', cam.fov)
        self.shader.uniform_float('bar_height', self.bar_height)
        self.shader.uniform_float('bar_width', self.bar_width)
        self.shader.uniform_float('elevation_position', self.elevation_position)
        self.shader.uniform_int('use_x', int(self.use_x))
        self.shader.uniform_int('use_y', int(self.use_y))

    def draw(self):
        super()._setup_draw()
        self._batch.draw(self.shader)
        cam = logic.getCurrentScene().active_camera
        # self.angle_x_label.text = int(degrees(Vector(cam.worldOrientation.to_euler()).z))
        super().draw()