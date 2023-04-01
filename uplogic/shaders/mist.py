from .shader import Filter2D
from mathutils import Vector
from bge import logic, render


glsl = """
in vec4 bgl_TexCoord;
#define gl_TexCoord glTexCoord
vec4 glTexCoord[4] = vec4[](bgl_TexCoord,bgl_TexCoord,bgl_TexCoord,bgl_TexCoord);
out vec4 fragColor;
#define gl_FragColor fragColor

uniform sampler2D bgl_RenderedTexture;
uniform sampler2D bgl_DepthTexture;
vec2 texcoord = vec2(gl_TexCoord[0]).st;
vec2 cancoord = vec2(gl_TexCoord[3]).st;

int model = 3; //mist model
int radial = 1;
uniform float density; //= 1.0;  // mist density
uniform float start; // = 0;  //distance at which mist starts
uniform vec3 color;
uniform float power;

uniform float znear; // = .1; //camera clipping start
uniform float zfar; // = 500; //camera clipping end
uniform float aspect; //camera aspect ratio
uniform float fov; //camera field of view

float linearize(float depth)
{
    return -zfar * znear / (depth * (zfar - znear) - zfar);
}

void main(void)
{    
    float depth = linearize(texture2D(bgl_DepthTexture,texcoord.xy).x);

    if (depth > zfar){
    //Clip the mist to allow for skyboxes
    depth = 0.0;
    }

    if (radial > 0){
        //Mist sphere
        float width = depth * tan(fov / 360 * 3.1415);
        float height = width / aspect;
        float y = (gl_TexCoord[0].st.y - 0.5) * 2.0 * height;
        float x = (gl_TexCoord[0].st.x - 0.5) * 2.0 * width;
        depth = length(vec3(x,y,depth));//pow(depth, 0.3333);
    }    


    vec4 mist = vec4(color.x, color.y, color.z, 1.0);
    float density2 = 1/density;
    float factor = 0.0;
    if (model == 1){
        //Linear Mist
        factor = (depth - start)/(density2*100);
    } else if (model == 2){
        //Quadratic Mist
        factor = max(depth - start, 0.0);
        factor = (factor * factor)/(density2*2000);
    } else if (model == 3){
        //Exponential Mist
        factor = 1.0 - exp(-(depth - start)*density*0.03);
    } else if (model == 4){
        //Exponential Squared Mist
        factor = max(depth - start, 0.0);
        factor = 1.0 - exp(-(factor * factor)*density*density*0.0003);
    }

    vec4 dif = texture(bgl_RenderedTexture, texcoord);

    gl_FragColor = mix(dif, mix(dif, mist, clamp(factor, 0.0, 1.0)), power);

}
"""


class Mist(Filter2D):

    def __init__(self, start=.1, density=0.5, color=(0.5, 0.7, 0.9), power=1.0, idx: int = None) -> None:
        cam = logic.getCurrentScene().active_camera
        self.settings = {
            'start': float(start),
            'density': float(density),
            'color': Vector(color),
            'power': float(power),
            'znear': cam.near,
            'zfar': cam.far,
            'fov': cam.fov,
            'aspect': render.getWindowWidth() / render.getWindowHeight()
        }
        super().__init__(glsl, idx, {
            'start': self.settings,
            'density': self.settings,
            'color': self.settings,
            'power': self.settings,
            'znear': self.settings,
            'zfar': self.settings,
            'fov': self.settings,
            'aspect': self.settings
        })

    def update(self):
        super().update()
        cam = logic.getCurrentScene().active_camera
        self.settings['znear'] = cam.near
        self.settings['zfar'] = cam.far
        self.settings['fov'] = cam.fov
        self.settings['aspect'] = render.getWindowWidth() / render.getWindowHeight()

    @property
    def start(self):
        return self.settings['start']

    @start.setter
    def start(self, val):
        self.settings['start'] = float(val)

    @property
    def density(self):
        return self.settings['density']

    @density.setter
    def density(self, val):
        self.settings['density'] = float(val)

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = val

    @property
    def color(self):
        return self.settings['color']

    @color.setter
    def color(self, val):
        self.settings['color'] = Vector(val).to_3d()
