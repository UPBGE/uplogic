from .widget import Widget
from bge import logic
from bge import render
from mathutils import Vector


class Compass(Widget):

    fragment_code = """
    uniform vec4 primary_color;
    uniform vec4 secondary_color;
    uniform vec4 tertiary_color;
    uniform vec2 screen;
    uniform vec3 camera_rotation;
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

        float degrees_z = degrees(camera_rotation.z);
        float degrees_x = degrees(camera_rotation.x);
        float x = ((.5 - pxpos[0]) * fov) + degrees_z;
        float y = ((pxpos[1] - .5) * fov * fov_factor) + degrees_x;

        int[4] main_directions = int[4](0, 90, -180, -90);
        int[4] secondary_directions = int[4](45, 135, -45, -135);
        int[32] tertiary_directions = int[32](
            10, 20, 30, 40, 50, 60, 70, 80, 100, 110, 120, 130, 140, 150, 160, 170,
            -10, -20, -30, -40, -50, -60, -70, -80, -100, -110, -120, -130, -140, -150, -160, -170
        );
        int[16] tertiary_directions_z = int[16](
            -10, -20, -30, -40, -50, -60, -70, -80, -100, -110, -120, -130, -140, -150, -160, -170
        );


        if (use_x == 1){
            for (int i = 0; i < main_directions.length(); i++){
                float xangle = abs(x + main_directions[i]);
                if (xangle > 180) {
                    xangle -= 180;
                }
                float center_fac = 1 - (2 * abs(.5 - pxpos[0]));
                if (xangle < _bar_width && abs(y - 90) < 1 * bar_height){
                    vec4 col = primary_color;
                    col[3] *= center_fac;
                    fragColor = col;
                    return;
                }
            }
            for (int i = 0; i < secondary_directions.length(); i++){
                float xangle = abs(x + secondary_directions[i]);
                if (xangle > 180) {
                    xangle -= 180;
                }
                float center_fac = 1 - (2 * abs(.5 - pxpos[0]));
                if (xangle < _bar_width * .75 && abs(y - 90) < 1 * bar_height * .5){
                    vec4 col = secondary_color;
                    col[3] *= center_fac;
                    fragColor = col;
                    return;
                }
            }
            for (int i = 0; i < tertiary_directions.length(); i++){
                float xangle = abs(x + tertiary_directions[i]);
                if (xangle > 180) {
                    xangle -= 180;
                }
                float center_fac = 1 - (2 * abs(.5 - pxpos[0]));
                if (xangle < _bar_width * .5 && abs(y - 90) < 1 * bar_height * .25){
                    vec4 col = tertiary_color;
                    col[3] *= center_fac;
                    fragColor = col;
                    return;
                }
            }
        }
        if (use_y == 1){
            for (int i = 0; i < tertiary_directions_z.length(); i++){
                float yangle = abs(y + tertiary_directions_z[i]);
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
            elevation_position=.5
        ):
        super().__init__()
        self.bar_height = bar_height
        self.bar_width = bar_width
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.tertiary_color = tertiary_color
        self.use_x = use_x
        self.use_y = use_y
        self.elevation_position = elevation_position

    def set_uniforms(self):
        self.shader.uniform_float("screen", Vector((
            render.getWindowWidth(), render.getWindowHeight()
        )))
        cam = logic.getCurrentScene().active_camera
        self.shader.uniform_float('camera_rotation', Vector(cam.worldOrientation.to_euler()))
        self.shader.uniform_float('primary_color', self.primary_color)
        self.shader.uniform_float('secondary_color', self.secondary_color)
        self.shader.uniform_float('tertiary_color', self.tertiary_color)
        self.shader.uniform_float('fov', cam.fov)
        self.shader.uniform_float('bar_height', self.bar_height)
        self.shader.uniform_float('bar_width', self.bar_width)
        self.shader.uniform_float('elevation_position', self.elevation_position)
        self.shader.uniform_int('use_x', int(self.use_x))
        self.shader.uniform_int('use_y', int(self.use_y))

    def draw(self):
        super()._setup_draw()
        self._batch.draw(self.shader)
        super().draw()