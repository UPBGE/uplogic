from .shader import Filter2D
from bge import logic, render
from mathutils import Vector


# glsl = """
# /* Original Code by existical @shadertoy: https://www.shadertoy.com/view/Xltfzj
# Modified by Iza Zed for UPBGE
# */

# uniform sampler2D bgl_RenderedTexture;
# uniform sampler2D bgl_DepthTexture;
# uniform float bgl_RenderedTextureWidth;
# uniform float bgl_RenderedTextureHeight;
# vec2 resolution = vec2(bgl_RenderedTextureWidth, bgl_RenderedTextureHeight);

# out vec4 fragColor;
# in vec4 bgl_TexCoord;

# vec2 texcoord = bgl_TexCoord.xy;

# uniform float samples;
# uniform float power;
# uniform float distance;
# uniform float fstop;

# uniform float znear; // = .1; //camera clipping start
# uniform float zfar; // = 500; //camera clipping end

# float linearize(float depth)
# {
#     return -zfar * znear / (depth * (zfar - znear) - zfar);
# }

# void main()
# {
#     float Pi = 6.28318530718;

#     float quality = 3.0;

#     vec2 uv = texcoord;
#     vec4 dcolor = clamp(texture(bgl_DepthTexture, uv), 0, .4);
#     dcolor += clamp(texture(bgl_DepthTexture, uv), .0, .4);

# //    for( float d=0.0; d<Pi; d+=Pi/samples)
# //    {
# //        for(float i = 1.0 / quality; i <= 1.0; i += 1.0 / quality)
# //        {
# //            dcolor = texture(bgl_DepthTexture, uv + vec2(cos(d),sin(d)) * vec2(.02)) * i;
# //        }
# //    }
# //    // dcolor /= quality * samples - 15.0;

#     float depth = linearize(dcolor.x);
#     fragColor = vec4(depth);
#     return;
#     depth = abs(distance - depth);

#     float dpower = (1 - depth) * power;

#     vec2 radius = dpower/resolution.xy * (depth * fstop);
#     radius.x = clamp(radius.x, 0.0, dpower / bgl_RenderedTextureWidth);
#     radius.y = clamp(radius.y, 0.0, dpower / bgl_RenderedTextureHeight);

#     vec4 color = texture(bgl_RenderedTexture, uv);

#     // Blur calculations
#     for( float d=0.0; d<Pi; d+=Pi/samples)
#     {
#         for(float i=1.0/quality; i<=1.0; i+=1.0/quality)
#         {
#             color += texture(bgl_RenderedTexture, uv+vec2(cos(d),sin(d)) * radius * i);
#         }
#     }
#     color /= quality * samples - 15.0;
#     fragColor = color;
# }"""


glsl = """
uniform sampler2D bgl_RenderedTexture;
uniform sampler2D bgl_DepthTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;

#define PI  3.14159265

float width = bgl_RenderedTextureWidth; //texture width
float height = bgl_RenderedTextureHeight; //texture height

in vec4 bgl_TexCoord;
vec2 texcoord = bgl_TexCoord.xy;

out vec4 fragColor

vec2 texel = vec2(1.0/width,1.0/height);

uniform float distance;  //external focal point value, but you may use autofocus option below
//float distance = 1;

//------------------------------------------
//user variables

uniform int samples; //samples on the first ring
int rings = 5; //ring count

uniform bool autofocus; //use autofocus in shader? disable if you use external distance value
vec2 focus = vec2(0.5,0.5); // autofocus point on screen (0.0,0.0 - left lower corner, 1.0,1.0 - upper right)
float range = 2.0; //focal range
uniform float fstop;
uniform float power; //clamp value of max blur

float threshold = 0.5; //highlight threshold;
float gain = 10.0; //highlight gain;

float bias = 0.4; //bokeh edge bias
float fringe = 0.5; //bokeh chromatic aberration/fringing

bool noise = true; //use noise instead of pattern for sample dithering
float namount = 0.0001; //dither amount

bool depthblur = true; //blur the depth buffer?
float dbsize = 2.0; //depthblursize

/*
next part is experimental
not looking good with small sample and ring count
looks okay starting from samples = 4, rings = 4
*/

bool pentagon = false; //use pentagon as bokeh shape?
float feather = 0.4; //pentagon shape feather

//------------------------------------------


float penta(vec2 coords) //pentagonal shape
{
	float scale = float(rings) - 1.3;
	vec4  HS0 = vec4( 1.0,         0.0,         0.0,  1.0);
	vec4  HS1 = vec4( 0.309016994, 0.951056516, 0.0,  1.0);
	vec4  HS2 = vec4(-0.809016994, 0.587785252, 0.0,  1.0);
	vec4  HS3 = vec4(-0.809016994,-0.587785252, 0.0,  1.0);
	vec4  HS4 = vec4( 0.309016994,-0.951056516, 0.0,  1.0);
	vec4  HS5 = vec4( 0.0        ,0.0         , 1.0,  1.0);

	vec4  one = vec4( 1.0 );

	vec4 P = vec4((coords),vec2(scale, scale)); 

	vec4 dist = vec4(0.0);
	float inorout = -4.0;

	dist.x = dot( P, HS0 );
	dist.y = dot( P, HS1 );
	dist.z = dot( P, HS2 );
	dist.w = dot( P, HS3 );

	dist = smoothstep( -feather, feather, dist );

	inorout += dot( dist, one );

	dist.x = dot( P, HS4 );
	dist.y = HS5.w - abs( P.z );

	dist = smoothstep( -feather, feather, dist );
	inorout += dist.x;

	return clamp( inorout, 0.0, 1.0 );
}

float bdepth(vec2 coords) //blurring depth
{
	float d = 0.0;
	float kernel[9];
	vec2 offset[9];

	vec2 wh = vec2(texel.x, texel.y) * dbsize;

	offset[0] = vec2(-wh.x,-wh.y);
	offset[1] = vec2( 0.0, -wh.y);
	offset[2] = vec2( wh.x -wh.y);

	offset[3] = vec2(-wh.x,  0.0);
	offset[4] = vec2( 0.0,   0.0);
	offset[5] = vec2( wh.x,  0.0);

	offset[6] = vec2(-wh.x, wh.y);
	offset[7] = vec2( 0.0,  wh.y);
	offset[8] = vec2( wh.x, wh.y);

	kernel[0] = 1.0/16.0;   kernel[1] = 2.0/16.0;   kernel[2] = 1.0/16.0;
	kernel[3] = 2.0/16.0;   kernel[4] = 4.0/16.0;   kernel[5] = 2.0/16.0;
	kernel[6] = 1.0/16.0;   kernel[7] = 2.0/16.0;   kernel[8] = 1.0/16.0;


	for( int i=0; i<9; i++ )
	{
		float tmp = texture2D(bgl_DepthTexture, coords + offset[i]).r;
		d += tmp * kernel[i];
	}

	return d;
}


vec3 color(vec2 coords,float blur) //processing the sample
{
	vec3 col = vec3(0.0);

	col.r = texture2D(bgl_RenderedTexture,coords + vec2(0.0,1.0)*texel*fringe*blur).r;
	col.g = texture2D(bgl_RenderedTexture,coords + vec2(-0.866,-0.5)*texel*fringe*blur).g;
	col.b = texture2D(bgl_RenderedTexture,coords + vec2(0.866,-0.5)*texel*fringe*blur).b;

	vec3 lumcoeff = vec3(0.299,0.587,0.114);
	float lum = dot(col.rgb, lumcoeff);
	float thresh = max((lum-threshold)*gain, 0.0);
	return col+mix(vec3(0.0),col,thresh*blur);
}

vec2 rand(in vec2 coord) //generating noise/pattern texture for dithering
{
	float noiseX = ((fract(1.0-coord.s*(width/2.0))*0.25)+(fract(coord.t*(height/2.0))*0.75))*2.0-1.0;
	float noiseY = ((fract(1.0-coord.s*(width/2.0))*0.75)+(fract(coord.t*(height/2.0))*0.25))*2.0-1.0;

	if (noise)
	{
		noiseX = clamp(fract(sin(dot(coord ,vec2(12.9898,78.233))) * 43758.5453),0.0,1.0)*2.0-1.0;
		noiseY = clamp(fract(sin(dot(coord ,vec2(12.9898,78.233)*2.0)) * 43758.5453),0.0,1.0)*2.0-1.0;
	}
	return vec2(noiseX,noiseY);
}

void main() 
{

	float depth = texture2D(bgl_DepthTexture, texcoord).x;
	float blur = 0.0;

	if (depthblur)
	{
		depth = bdepth(texcoord);
	}

	blur = clamp((abs(depth - distance)/fstop)*100.0,-power,power);

	if (autofocus)
	{
		float fDepth = texture2D(bgl_DepthTexture, focus).x;
		blur = clamp((abs(depth - fDepth)/fstop)*100.0,-power,power);
	}

	vec2 noise = rand(texcoord)*namount*blur;

	float w = (1.0/width)*blur+noise.x;
	float h = (1.0/height)*blur+noise.y;

	vec3 col = texture2D(bgl_RenderedTexture, texcoord).rgb;
	float s = 1.0;

	int ringsamples;

	for (int i = 1; i <= rings; i += 1)
	{   
		ringsamples = i * samples;
		 
		for (int j = 0 ; j < ringsamples ; j += 1)   
		{
			float step = PI*2.0 / float(ringsamples);
			float pw = (cos(float(j)*step)*float(i));
			float ph = (sin(float(j)*step)*float(i));
			float p = 1.0;
			if (pentagon)
			{ 
			p = penta(vec2(pw,ph));
			}
			col += color(texcoord + vec2(pw*w,ph*h),blur)*mix(1.0,(float(i))/(float(rings)),bias)*p;  
			s += 1.0*mix(1.0,(float(i))/(float(rings)),bias)*p;   
		}
	}

	col /= s;   

	fragColor.rgb = col;
	fragColor.a = 1.0;
}
"""


class DoF(Filter2D):

        
    def __init__(self, distance=1.0, autofocus=False, power=1.0, fstop=1, samples=16, idx: int = None) -> None:
        cam = logic.getCurrentScene().active_camera
        self.settings = {
            'distance': float(distance),
            'power': float(power),
            'fstop': float(fstop),
            'samples': int(samples),
            'autofocus': bool(autofocus)
            # 'znear': cam.near,
            # 'zfar': cam.far
        }
        super().__init__(glsl, idx, {
            'distance': self.settings,
            'power': self.settings,
            'fstop': self.settings,
            'samples': self.settings,
            'autofocus': self.settings
            # 'znear': self.settings,
            # 'zfar': self.settings
        })

    def update(self):
        super().update()
        cam = logic.getCurrentScene().active_camera
        self.settings['znear'] = cam.near
        self.settings['zfar'] = cam.far

    @property
    def distance(self):
        return self.settings['distance']

    @distance.setter
    def distance(self, val):
        self.settings['distance'] = float(val)

    @property
    def autofocus(self):
        return self.settings['autofocus']

    @autofocus.setter
    def autofocus(self, val):
        self.settings['autofocus'] = bool(val)

    @property
    def fstop(self):
        return self.settings['fstop']

    @fstop.setter
    def fstop(self, val):
        self.settings['fstop'] = float(val)

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = val

    @property
    def samples(self):
        return self.settings['samples']

    @samples.setter
    def samples(self, val):
        self.settings['samples'] = int(val)
