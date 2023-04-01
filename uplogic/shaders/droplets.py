from .shader import Filter2D
from bge import logic
from mathutils import Vector


glsl = """
/* Original Code by martins upitis @youtube: https://www.youtube.com/watch?v=UkskiSza4p0
Modified by Iza Zed for uplogic
*/

in vec4 bgl_TexCoord;
#define gl_TexCoord glTexCoord
vec4 glTexCoord[4] = vec4[](bgl_TexCoord,bgl_TexCoord,bgl_TexCoord,bgl_TexCoord);

out vec4 fragColor;
#define gl_FragColor fragColor

uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;

uniform float timer, time, randomtime, blur;
uniform vec3 color;

vec2 texcoord = vec2(gl_TexCoord[0]).st;

const float permTexUnit = 1.0/256.0;		// Perm texture texel-size
const float permTexUnitHalf = 0.5/256.0;	// Half perm texture texel-size

float width = bgl_RenderedTextureWidth;
float height = bgl_RenderedTextureHeight;

//a random texture generator, but you can also use a pre-computed perturbation texture
vec4 rnm(in vec2 tc) 
{
    float noise =  sin(dot(tc ,vec2(12.9898,78.233))) * 43758.5453;

    float noiseR =  fract(noise)*2.0-1.0;
    float noiseG =  fract(noise*1.2154)*2.0-1.0; 
    float noiseB =  fract(noise*1.3453)*2.0-1.0;
    float noiseA =  fract(noise*1.3647)*2.0-1.0;
    
    return vec4(noiseR,noiseG,noiseB,noiseA);
}

vec3 fblur(vec2 uv){
    float samples = 16;
    vec2 resolution = vec2(bgl_RenderedTextureWidth, bgl_RenderedTextureHeight);
    float Pi = 6.28318530718;

    float quality = 3.0;
   
    vec2 radius = blur/resolution.xy;

    vec3 frag = texture(bgl_RenderedTexture, uv).rgb;

    for( float d=0.0; d<Pi; d+=Pi/samples)
    {
		for(float i = 1.0/quality; i<=1.0; i+=1.0/quality)
        {
			frag += texture(bgl_RenderedTexture, uv+vec2(cos(d),sin(d)) * radius * i).rgb;
        }
    }
    frag /= quality * samples - 15.0;
    return frag;
}

float fade(in float t) {
    return t*t*t*(t*(t*6.0-15.0)+10.0);
}

float pnoise3D(in vec3 p)
{
    vec3 pi = permTexUnit*floor(p)+permTexUnitHalf; // Integer part, scaled so +1 moves permTexUnit texel
    // and offset 1/2 texel to sample texel centers
    vec3 pf = fract(p);     // Fractional part for interpolation

    // Noise contributions from (x=0, y=0), z=0 and z=1
    float perm00 = rnm(pi.xy).a ;
    vec3  grad000 = rnm(vec2(perm00, pi.z)).rgb * 4.0 - 1.0;
    float n000 = dot(grad000, pf);
    vec3  grad001 = rnm(vec2(perm00, pi.z + permTexUnit)).rgb * 4.0 - 1.0;
    float n001 = dot(grad001, pf - vec3(0.0, 0.0, 1.0));

    // Noise contributions from (x=0, y=1), z=0 and z=1
    float perm01 = rnm(pi.xy + vec2(0.0, permTexUnit)).a ;
    vec3  grad010 = rnm(vec2(perm01, pi.z)).rgb * 4.0 - 1.0;
    float n010 = dot(grad010, pf - vec3(0.0, 1.0, 0.0));
    vec3  grad011 = rnm(vec2(perm01, pi.z + permTexUnit)).rgb * 4.0 - 1.0;
    float n011 = dot(grad011, pf - vec3(0.0, 1.0, 1.0));

    // Noise contributions from (x=1, y=0), z=0 and z=1
    float perm10 = rnm(pi.xy + vec2(permTexUnit, 0.0)).a ;
    vec3  grad100 = rnm(vec2(perm10, pi.z)).rgb * 4.0 - 1.0;
    float n100 = dot(grad100, pf - vec3(1.0, 0.0, 0.0));
    vec3  grad101 = rnm(vec2(perm10, pi.z + permTexUnit)).rgb * 4.0 - 1.0;
    float n101 = dot(grad101, pf - vec3(1.0, 0.0, 1.0));

    // Noise contributions from (x=1, y=1), z=0 and z=1
    float perm11 = rnm(pi.xy + vec2(permTexUnit, permTexUnit)).a ;
    vec3  grad110 = rnm(vec2(perm11, pi.z)).rgb * 4.0 - 1.0;
    float n110 = dot(grad110, pf - vec3(1.0, 1.0, 0.0));
    vec3  grad111 = rnm(vec2(perm11, pi.z + permTexUnit)).rgb * 4.0 - 1.0;
    float n111 = dot(grad111, pf - vec3(1.0, 1.0, 1.0));

    // Blend contributions along x
    vec4 n_x = mix(vec4(n000, n001, n010, n011), vec4(n100, n101, n110, n111), fade(pf.x));

    // Blend contributions along y
    vec2 n_xy = mix(n_x.xy, n_x.zw, fade(pf.y));

    // Blend contributions along z
    float n_xyz = mix(n_xy.x, n_xy.y, fade(pf.z));

    // We're done, return the final noise value.
    return n_xyz;
}

vec2 coordRot(in vec2 tc, in float angle)
{
    float rotX = ((tc.x*2.0-1.0)*(width/height)*cos(angle)) - ((tc.y*2.0-1.0)*sin(angle));
    float rotY = ((tc.y*2.0-1.0)*cos(angle)) + ((tc.x*2.0-1.0)*(width/height)*sin(angle));
    rotX = ((rotX/(width/height))*0.5+0.5);
    rotY = rotY*0.5+0.5;
    return vec2(rotX,rotY);
}

void main(void)
{
    if (time > 10){
        gl_FragColor = texture(bgl_RenderedTexture, texcoord);
        return;
    }
    float grainsize = 100.0;
    float fade = 12;
    vec2 distortFade = vec2(0.0);
    distortFade.s = clamp(texcoord.s*fade,0.0,1.0);
    distortFade.s -= clamp(1.0-(1.0-texcoord.s)*fade,0.0,1.0);
    distortFade.t = clamp(texcoord.t*fade,0.0,1.0);
    distortFade.t -= clamp(1.0-(1.0-texcoord.t)*fade,0.0,1.0); 

    vec2 rotCoordsR = texcoord;
    
    float dfade = 1.0-pow((1.0-distortFade.s*distortFade.t),2.0);
    float noiz = 0.0;
    float drop = 0.0;

    float timeslow = time*0.02;
    float timefaster = time*0.5;
    
    if (time > 0.0 && time < 4.0)
    {
        noiz += pnoise3D(vec3(texcoord*vec2(width/90.0,height/200.0)+vec2(0.0,timer*0.6),1.0+timer*0.2))*0.25;
        noiz += pnoise3D(vec3(texcoord*vec2(width/1200.0,height/1800.0)+vec2(0.0,timer*0.5),3.0+timer*0.3))*0.75;
    }
    
    if (time > 0.0 && time < 100.0)
    {
        drop += pnoise3D(vec3(texcoord*vec2(width/40.0,height/60.0),randomtime/8.0+timer*0.02))*0.2;
        drop += pnoise3D(vec3(texcoord*vec2(width/80.0,height/200.0),randomtime*2.1+timer*0.03))*0.25;
    }
        
    float dropfade = clamp(time*10.0,0.0,1.0);
    
    float drops = clamp(smoothstep(0.0+timefaster,0.5+timefaster,noiz*0.5+0.5),0.0,1.0);
    float droplet = clamp(smoothstep(0.75+timeslow,1.0+timeslow,drop*0.5+0.5),0.0,1.0);
    
    droplet = pow(clamp(droplet+drops,0.0,1.0),0.1)*3.0;
    float dropletmask = smoothstep(0.77+timeslow,0.79+timeslow,drop*0.5+0.5);

    float mask = smoothstep(0.02+timefaster,0.03+timefaster,noiz*0.5+0.5);
    

    vec2 droplets = vec2(dFdx(texcoord+droplet).r,dFdy(texcoord+droplet).g);		

    vec2 dropcoordR;
    vec2 dropcoordG;
    vec2 dropcoordB;

    droplets = droplets*dfade;
    
    dropcoordR = (texcoord-droplets*1.1);
    dropcoordG = (texcoord-droplets*1.2);	
    dropcoordB = (texcoord-droplets*1.3);	

    vec3 frag = texture(bgl_RenderedTexture, texcoord).rgb;

    vec3 dropletcolor = vec3(0.0);
    if (blur != 0.0){
        dropletcolor.r = fblur(dropcoordR).r * color.x;
        dropletcolor.g = fblur(dropcoordG).g * color.y;
        dropletcolor.b = fblur(dropcoordB).b * color.z;
    } else {
        dropletcolor.r = texture(bgl_RenderedTexture, dropcoordR).r * color.x;
        dropletcolor.g = texture(bgl_RenderedTexture, dropcoordG).g * color.y;
        dropletcolor.b = texture(bgl_RenderedTexture, dropcoordB).b * color.z;
    }
    
    vec3 final = mix(frag, dropletcolor, clamp(dropletmask+mask,0.0,1.0)*dropfade);
    gl_FragColor = vec4(final,1.0);
}"""


class Droplets(Filter2D):

    def __init__(self, color=(1, 1, 1), speed=1.0, blur=0.0, idx: int = None) -> None:
        now = logic.getRealTime()
        self.speed = speed
        self.settings = {
            'blur': float(blur),
            'color': Vector(color),
            'timer': float(now),
            'time': float(100.0),
            'randomtime': float(logic.getRandomFloat())
        }
        self._last_time = now
        self.randomize()
        super().__init__(glsl, idx, {
            'blur': self.settings,
            'color': self.settings,
            'timer': self.settings,
            'time': self.settings,
            'randomtime': self.settings
        })

    def update(self):
        now = logic.getRealTime()
        diff = (now - self._last_time) * self.speed
        self.timer += diff
        self._last_time = now
        self.time += diff
        super().update()

    def randomize(self):
        self.randomtime = (logic.getRandomFloat()*5)*2.0-1.0

    def restart(self):
        self.randomize()
        self.time = 0.0
        self.timer = 0.0

    @property
    def blur(self):
        return self.settings['blur']

    @blur.setter
    def blur(self, val):
        self.settings['blur'] = float(val)

    @property
    def color(self):
        return self.settings['color']

    @color.setter
    def color(self, val):
        self.settings['color'] = Vector(val).to_3d()

    @property
    def timer(self):
        return self.settings['timer']

    @timer.setter
    def timer(self, val):
        self.settings['timer'] = float(val)

    @property
    def randomtime(self):
        return self.settings['randomtime']

    @randomtime.setter
    def randomtime(self, val):
        self.settings['randomtime'] = float(val)

    @property
    def time(self):
        return self.settings['time']

    @time.setter
    def time(self, val):
        self.settings['time'] = float(val)