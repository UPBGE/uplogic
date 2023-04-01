from .shader import Filter2D
from bge import logic


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

uniform float timer, resettimer, randomtime, power;

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
    vec4 original = gl_FragColor = texture2D(bgl_RenderedTexture, texcoord);
    float grainsize = 100.0;
    //texture edge bleed removal
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

    float resettimerslow = resettimer*0.02;
    float resettimerfaster = resettimer*0.5;
    
    if (resettimer > 0.0 && resettimer < 4.0)
    {
    //noiz += pnoise3D(vec3(texcoord*vec2(width/50.0,height/80.0)+vec2(0.0,timer*0.8),timer*0.2))*0.1;
    noiz += pnoise3D(vec3(texcoord*vec2(width/90.0,height/200.0)+vec2(0.0,timer*0.6),1.0+timer*0.2))*0.25;
    //noiz += pnoise3D(vec3(texcoord*vec2(width/200.0,height/400.0)+vec2(0.0,timer*0.4),2.0+timer*0.4))*0.25;
    noiz += pnoise3D(vec3(texcoord*vec2(width/1200.0,height/1800.0)+vec2(0.0,timer*0.5),3.0+timer*0.3))*0.75;
    }
    
    if (resettimer > 0.0 && resettimer < 100.0)
    {
    drop += pnoise3D(vec3(texcoord*vec2(width/40.0,height/60.0),randomtime/8.0+timer*0.02))*0.2;
    drop += pnoise3D(vec3(texcoord*vec2(width/80.0,height/200.0),randomtime*2.1+timer*0.03))*0.25;
    //drop += pnoise3D(vec3(texcoord*vec2(width/200.0,height/400.0),randomtime*0.23+timer*0.04))*0.2;
    //drop += pnoise3D(vec3(texcoord*vec2(width/800.0,height/1800.0),randomtime*1.64+timer*0.05))*0.1;
    }
        
    float dropfade = clamp(resettimer*10.0,0.0,1.0);
    
    float drops = clamp(smoothstep(0.0+resettimerfaster,0.5+resettimerfaster,noiz*0.5+0.5),0.0,1.0);
    float droplet = clamp(smoothstep(0.75+resettimerslow,1.0+resettimerslow,drop*0.5+0.5),0.0,1.0);
    
    droplet = pow(clamp(droplet+drops,0.0,1.0),0.1)*3.0;
    float dropletmask = smoothstep(0.77+resettimerslow,0.79+resettimerslow,drop*0.5+0.5);

    //drops = pow(drops,0.1)*2.0;
    float mask = smoothstep(0.02+resettimerfaster,0.03+resettimerfaster,noiz*0.5+0.5);	

    vec2 wave;
    
    vec2 wavecoordR;
    vec2 wavecoordG;
    vec2 wavecoordB;
    vec2 dropcoordR;
    vec2 dropcoordG;	
    vec2 dropcoordB;

    if (resettimer < 1.0)
    {
    wave.x = sin((texcoord.x-texcoord.y*2.0)-timer*1.5)*0.25;
    wave.x += cos((texcoord.y*4.0-texcoord.x*6.0)+timer*4.2)*0.5;
    wave.x += sin((texcoord.x*9.0+texcoord.y*8.0)+timer*3.5)*0.25;
    
    wave.y = sin((texcoord.x*2.0+texcoord.x*2.5)+timer*2.5)*0.25;
    wave.y += cos((texcoord.y*3.0+texcoord.x*6.0)-timer*2.5)*0.5;
    wave.y += sin((texcoord.x*11.0-texcoord.y*12.0)+timer*4.5)*0.25;
    }
    
    wave = wave*dfade;

    wavecoordR = texcoord-wave*0.004;
    wavecoordG = texcoord-wave*0.006;	
    wavecoordB = texcoord-wave*0.008;

    vec3 color = texture2D(bgl_RenderedTexture, texcoord).rgb;
    
    vec3 wavecolor = vec3(0.0);
    wavecolor.r = texture2D(bgl_RenderedTexture, wavecoordR).r;
    wavecolor.g = texture2D(bgl_RenderedTexture, wavecoordG).g;
    wavecolor.b = texture2D(bgl_RenderedTexture, wavecoordB).b;
    
    vec3 final = mix(wavecolor,color,dropfade);
//    final = wavecolor;


    gl_FragColor = mix(original, vec4(final,1.0), power);
    
}"""


class Distort(Filter2D):

    def __init__(self, power=1.0, speed=1.0, idx: int = None) -> None:
        now = logic.getRealTime()
        self.speed = speed
        self.settings = {'power': float(power), 'timer': now, 'resettimer': 0.0, 'randomtime': logic.getRandomFloat()}
        self._last_time = now
        self.randomize()
        super().__init__(glsl, idx, {'power': self.settings, 'timer': self.settings, 'resettimer': self.settings, 'randomtime': self.settings})

    def update(self):
        now = logic.getRealTime()
        self.timer += (now - self._last_time) * self.speed
        self._last_time = now
        self.resettimer += (now - self._last_time) * self.speed
        super().update()

    def randomize(self):
        self.randomtime = (logic.getRandomFloat()*5)*2.0-1.0

    def restart(self):
        self.resettimer = 0.0
        self.timer = 0.0

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
    def resettimer(self):
        return self.settings['resettimer']

    @resettimer.setter
    def resettimer(self, val):
        self.settings['resettimer'] = float(val)

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = float(val)