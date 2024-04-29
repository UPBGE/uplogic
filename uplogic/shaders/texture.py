from .shader import Filter2D
import bpy, bge
from mathutils import Vector
from ..console import error


glsl = """
uniform sampler2D bgl_RenderedTexture;
uniform sampler2D tex;
uniform float opacity;
uniform vec2 pos;
uniform vec2 size;

in vec4 bgl_TexCoord;

out vec4 fragColor;


float map_range(float value, float in_min, float in_max, float out_min, float out_max){
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}


void main()
{

    vec2 texcoord = bgl_TexCoord.xy;
    float opa = opacity;

    if (texcoord.x < pos.x || texcoord.x > pos.x + size.x || texcoord.y < pos.y || texcoord.y > pos.y + size.y){
        opa = 0;
    }

    vec2 texMap = vec2(
        map_range(texcoord.x, pos.x, pos.x + size.x, 0, 1),
        map_range(texcoord.y, pos.y, pos.y + size.y, 0, 1)
    );
	fragColor = mix(
        texture(bgl_RenderedTexture, texcoord),
        texture(tex, texMap),
        opa
    );
}
"""


class Texture(Filter2D):

    def __init__(self, texture: bpy.types.Image = None, opacity: float = 1.0, pos=Vector((0, 0)), size=Vector((1, 1)), idx: int = None) -> None:
        if not isinstance(texture, bpy.types.Image):
            error("'Texture': first argument requires an object of type 'bpy.types.Image'!")
            return
        texture.gl_load()
        self.free_textures = True
        self.settings = {'tex': texture, 'opacity': float(opacity), 'pos': Vector(pos), 'size': Vector(size)}
        super().__init__(glsl, idx, {'tex': self.settings, 'opacity': self.settings, 'pos': self.settings, 'size': self.settings})

    @property
    def texture(self):
        return self.settings['tex']

    @texture.setter
    def texture(self, val):
        if self.free_textures:
            self.settings['tex'].gl_free()
        if not isinstance(val, bpy.types.Image):
            raise TypeError
        val.gl_load()
        self.settings['tex'] = val

    @property
    def opacity(self):
        return self.settings['opacity']

    @opacity.setter
    def opacity(self, val):
        self.settings['opacity'] = float(val)

    @property
    def pos(self):
        return self.settings['pos']

    @pos.setter
    def pos(self, val):
        self.settings['pos'] = Vector(val).to_2d()

    @property
    def size(self):
        return self.settings['size']

    @size.setter
    def size(self, val):
        self.settings['size'] = Vector(val).to_2d()
