from .shader import Filter2D
from bge import logic


glsl = """
/*
SSAO GLSL shader v1.2
assembled by Martins Upitis (martinsh) (devlog-martinsh.blogspot.com)
original technique is made by Arkano22 (www.gamedev.net/topic/550699-ssao-no-halo-artifacts/)

changelog:
1.2 - added fog calculation to mask AO. Minor fixes.
1.1 - added spiral sampling method from here:
(http://www.cgafaq.info/wiki/Evenly_distributed_points_on_sphere)
*/
uniform sampler2D bgl_DepthTexture;
uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;
in vec4 bgl_TexCoord;

#define PI    3.14159265

float width = bgl_RenderedTextureWidth; //texture width
float height = bgl_RenderedTextureHeight; //texture height

vec2 texCoord = bgl_TexCoord.xy;

//------------------------------------------
//general stuff

//make sure that these two values are the same for your camera, otherwise distances will be wrong.

uniform float znear; //Z-near
uniform float zfar; //Z-far

uniform float power;

//user variables
int samples = 32; //ao sample count

float radius = 5.0; //ao radius
float aoclamp = 0.5; //depth clamp - reduces haloing at screen edges
bool noise = true; //use noise instead of pattern for sample dithering
float noiseamount = 0.0002; //dithering amount

float diffarea = 0.4; //self-shadowing reduction
float gdisplace = 0.5; //gauss bell center
float aowidth = 1.0; //gauss bell width

bool mist = true; //use mist?
float miststart = 0.0; //mist start
float mistend = 100.0; //mist end

bool onlyAO = false; //use only ambient occlusion pass?
float lumInfluence = 0.7; //how much luminance affects occlusion

//--------------------------------------------------------

vec2 rand(vec2 coord) //generating noise/pattern texture for dithering
{
	float noiseX = ((fract(1.0-coord.s*(width/2.0))*0.25)+(fract(coord.t*(height/2.0))*0.75))*2.0-1.0;
	float noiseY = ((fract(1.0-coord.s*(width/2.0))*0.75)+(fract(coord.t*(height/2.0))*0.25))*2.0-1.0;
	
	if (noise)
	{
		noiseX = clamp(fract(sin(dot(coord ,vec2(12.9898,78.233))) * 43758.5453),0.0,1.0)*2.0-1.0;
		noiseY = clamp(fract(sin(dot(coord ,vec2(12.9898,78.233)*2.0)) * 43758.5453),0.0,1.0)*2.0-1.0;
	}
	return vec2(noiseX,noiseY)*noiseamount;
}

float doMist()
{
	float zdepth = texture2D(bgl_DepthTexture,texCoord.xy).x;
	float depth = -zfar * znear / (zdepth * (zfar - znear) - zfar);
	return clamp((depth-miststart)/mistend,0.0,1.0);
}

float readDepth(in vec2 coord) 
{
	coord.x = clamp(coord.x,0.001,0.999);
    coord.y = clamp(coord.y,0.001,0.999);
	return (2.0 * znear) / (zfar + znear - texture2D(bgl_DepthTexture, coord ).x * (zfar-znear));
}

float compareDepths(in float depth1, in float depth2,inout int far)
{   
	float garea = aowidth; //gauss bell width    
	float diff = (depth1 - depth2)*100.0; //depth difference (0-100)
	//reduce left bell width to avoid self-shadowing 
	if (diff<gdisplace) {
		garea = diffarea;
	} else {
		far = 1;
	}
	
	float gauss = pow(2.7182,-2.0*(diff-gdisplace)*(diff-gdisplace)/(garea*garea));
	return gauss;
}   

float calAO(float depth,float dw, float dh)
{   
	//float dd = (1.0-depth)*radius;
	float dd = radius;
	float temp = 0.0;
	float temp2 = 0.0;
	float coordw = bgl_TexCoord.x + dw*dd;
	float coordh = bgl_TexCoord.y + dh*dd;
	float coordw2 = bgl_TexCoord.x - dw*dd;
	float coordh2 = bgl_TexCoord.y - dh*dd;
	
	vec2 coord = vec2(coordw , coordh);
	vec2 coord2 = vec2(coordw2, coordh2);
	
	int far = 0;
	temp = compareDepths(depth, readDepth(coord),far);
	//DEPTH EXTRAPOLATION:
	if (far > 0)
	{
		temp2 = compareDepths(readDepth(coord2),depth,far);
		temp += (1.0-temp)*temp2;
	}
	
	return temp;
} 

void main(void)
{
	vec2 noise = rand(texCoord); 
	float depth = readDepth(texCoord);
	
	float w = (1.0 / width)/clamp(depth,aoclamp,1.0)+(noise.x*(1.0-noise.x));
	float h = (1.0 / height)/clamp(depth,aoclamp,1.0)+(noise.y*(1.0-noise.y));
	
	float pw;
	float ph;
	
	float ao;
	
	float dl = PI*(3.0-sqrt(5.0));
	float dz = 1.0/float(samples);
	float l = 0.0;
	float z = 1.0 - dz/2.0;
	
	for (int i = 0; i <= samples; i ++)
	{     
		float r = sqrt(1.0-z);
		
		pw = cos(l)*r;
		ph = sin(l)*r;
		ao += calAO(depth,pw*w,ph*h);        
		z = z - dz;
		l = l + dl;
	}
	
	ao /= float(samples);
	ao = 1.0-ao;	
	
	if (mist)
	{
	ao = mix(ao, 1.0,doMist());
	}
	
	vec3 color = texture(bgl_RenderedTexture,texCoord).rgb;
	
	vec3 lumcoeff = vec3(0.299,0.587,0.114);
	float lum = dot(color.rgb, lumcoeff);
	vec3 luminance = vec3(lum, lum, lum);
	
	vec3 final = vec3(color*mix(vec3(ao),vec3(1.0),luminance*lumInfluence));//mix(color*ao, white, luminance)
	
	if (onlyAO)
	{
	final = vec3(mix(vec3(ao),vec3(1.0),luminance*lumInfluence)); //ambient occlusion only
	}
	
	
	gl_FragColor = mix(vec4(color, 1.0), vec4(final, 1.0), power);
	
}
"""


class SSAO(Filter2D):

    def __init__(self, power=1.0, idx: int = None) -> None:
        cam = logic.getCurrentScene().active_camera
        self.settings = {
			'power': float(power),
            'znear': cam.near,
            'zfar': cam.far
        }
        super().__init__(glsl, idx, {
			'power': self.settings,
            'znear': self.settings,
            'zfar': self.settings
        })

    @property
    def power(self):
        return self.settings['power']

    @power.setter
    def power(self, val):
        self.settings['power'] = val

    def update(self):
        super().update()
        cam = logic.getCurrentScene().active_camera
        self.settings['znear'] = cam.near
        self.settings['zfar'] = cam.far
