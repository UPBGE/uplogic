from .shader import Filter2D
from bge import logic


glsl = """
// Shader authored by LieGri (https://blenderartists.org/t/bge-hbao-ambient-occlusion-shader/690374)
// Modified for UPBGE 0.3+ by Iza Zed

uniform sampler2D bgl_DepthTexture;
uniform sampler2D bgl_RenderedTexture;
uniform float bgl_RenderedTextureWidth;
uniform float bgl_RenderedTextureHeight;
uniform float power;
in vec4 bgl_TexCoord;
out vec4 fragColor;

//THIS NEEDS TO MATCH YOUR CAMERA SETTINGS---------------------
uniform float znear;                    //Z-near
uniform float zfar;                     //Z-far
uniform float fov;                      //FoV
//-------------------------------------------------------------

//USER VARIABLES-----------------------------------------------
const float intensity = 1.0;            //Intensity of the AO effect
const float sampleRadius = 8.0;         //Radius of the AO, bigger values need more performance


const float sampleDirections = 5.0;    //Main sample count, affects performance heavily 
const float sampleSteps = 64.0;         //SubSample count, sometimes higher values are faster


const bool useAttenuation = true;      //Applies attenuation to each AO sample, different values look better depending on your scene
const float attenuationScale = 0.7;     //Depth scale of the attenuation, different values look better depending on your scene


const float angleBias = .2;            //Brightens up the AO effect to reduce noise and artifacts


const bool noise = false;               //Use noise instead of pattern for sample dithering, much slower but more accurate
const float noiseamount = .1;          //Per-Pixel noise amount, bigger values need more performance
const float jitterAmount = .1;         //Per-Sample noise amount, bigger values need more performance


const float lumInfluence = 0.0;         //Influence of the luminance on the AO effect


const bool onlyAO = false;               //Only show AO pass for debugging
const bool externalBlur = false;         //Store AO in alpha pass for a later blur
//-------------------------------------------------------------


float width = bgl_RenderedTextureWidth;
float height = bgl_RenderedTextureHeight;


vec2 texCoord = bgl_TexCoord.xy;


float aspectratio = width/height;
float thfov = tan(fov * 0.0087266462597222);
const float TWO_PI = 6.283185307;


float linearize_depth(vec2 uv){
    float n = .1;
    float f = 100.0;
    float z = texture(bgl_DepthTexture, uv).x;
    return (2.0 * n) / (f + n - z * (f - n));
}


vec3 getLinearColor(vec2 coord)
{    
    vec3 C = vec3(texture(bgl_RenderedTexture, coord));
    C.r = pow(C.r, 2.2);
    C.g = pow(C.g, 2.2);
    C.b = pow(C.b, 2.2);
    return C.rgb;
}


vec3 sRGBToLinear(vec3 C)
{
    C.r = pow(C.r, 2.2);
    C.g = pow(C.g, 2.2);
    C.b = pow(C.b, 2.2);
    return C.rgb;
}


vec3 linearTosRGB(vec3 C)
{
    C.r = pow(C.r, 0.45454545);
    C.g = pow(C.g, 0.45454545);
    C.b = pow(C.b, 0.45454545);
    return C.rgb;
}


float getLinearDepth(vec2 coord)
{
    float zdepth = texture(bgl_DepthTexture,coord).x;
    return zfar*znear / (zfar + zdepth * (znear - zfar));
}


vec3 getViewVector(vec2 coord)
{
    vec2 ndc = (coord * 2.0 - 1.0);
    return vec3(ndc.x*thfov, ndc.y*thfov/aspectratio, 1.0);
}


vec3 getViewPosition(vec2 coord)
{
    return getViewVector(coord) * getLinearDepth(coord);
}


vec3 getViewNormal(vec2 coord)
{
    float pW = 1.0/width;
    float pH = 1.0/height;
    
    vec3 p1 = getViewPosition(coord+vec2(pW,0.0)).xyz;
    vec3 p2 = getViewPosition(coord+vec2(0.0,pH)).xyz;
    vec3 p3 = getViewPosition(coord+vec2(-pW,0.0)).xyz;
    vec3 p4 = getViewPosition(coord+vec2(0.0,-pH)).xyz;


    vec3 vP = getViewPosition(coord);

    vec3 dx = vP-p1;
    vec3 dy = p2-vP;
    vec3 dx2 = p3-vP;
    vec3 dy2 = vP-p4;

    if(length(dx2)<length(dx)&&coord.x-pW>=0||coord.x+pW>1) {
    dx = dx2;
    }
    if(length(dy2)<length(dy)&&coord.y-pH>=0||coord.y+pH>1) {
    dy = dy2;
    }

    return normalize(cross( dx , dy ));
}


float rand(vec2 co)
{
    if (noise) {
        return fract(sin(dot(co.xy,vec2(12.9898,78.233)*3.0)) * 43758.5453);
    } else {
        return ((fract(1.0-co.s*(width/2.0))*0.3)+(fract(co.t*(height/2.0))*0.6))*2.0-1.0;
    }
}


vec2 rand2D(vec2 coord) //generating noise/pattern texture for dithering
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


mat4 getViewProjectionMatrix()
{
    mat4 result;
    
    float frustumDepth = zfar - znear;
    float oneOverDepth = 1 / frustumDepth;


    result[0][0] = 1 / thfov;
    result[1][1] = aspectratio * result[0][0];
    result[2][2] = zfar * oneOverDepth;
    result[2][3] = 1;
    result[3][2] = (-zfar * znear) * oneOverDepth;

    return result;
}


vec2 ComputeFOVProjection(vec3 pos, mat4 VPM)
{
    vec4 offset = vec4(pos, 1.0);
    offset = VPM * offset;
    offset.xy /= offset.w;
    return offset.xy * 0.5 + 0.5;
}


void main()
{
    mat4 VPM = getViewProjectionMatrix();
    mat4 viewProjectionInverseMatrix  = inverse(VPM);

    vec3 color = texture(bgl_RenderedTexture, bgl_TexCoord.xy).rgb;
    float d = linearize_depth(texCoord);
    if (d >= 0.9){
        fragColor.rgb = color;
        fragColor.a = 1;
        return;
    }

    vec3 originVS = getViewPosition(texCoord);
    vec3 normalVS = getViewNormal(texCoord);

    float radiusSS = 0.0;
    float radiusWS = 0.0;

    radiusSS = sampleRadius;
    vec4 temp0 = viewProjectionInverseMatrix * vec4(0.0, 0.0, -1.0, 1.0);
    vec3 out0 = temp0.xyz;
    vec4 temp1 = viewProjectionInverseMatrix * vec4(radiusSS, 0.0, -1.0, 1.0);
    vec3 out1 = temp1.xyz;

    radiusWS = min(tan(radiusSS * fov * 0.0087266462597222) * originVS.z, length(out1 - out0));

    /*if (radiusSS < 1.0 / width) {
        fragColor.rgb = color;
        fragColor.a = 1.0;
        return;
    }*/

    const float theta = TWO_PI / float(sampleDirections);
    float cosTheta = cos(theta);
    float sinTheta = sin(theta);

    mat2 deltaRotationMatrix = mat2(cosTheta, -sinTheta, sinTheta, cosTheta);
    vec2 deltaUV = vec2(1.0, 0.0) * (radiusSS / (float(sampleDirections * sampleSteps) + 1.0));

    vec2 sampleNoise = rand2D(texCoord);
    mat2 rotationMatrix = mat2(sampleNoise.x, -sampleNoise.y, 
                               sampleNoise.y,  sampleNoise.x);

    deltaUV = rotationMatrix * deltaUV;

    float occlusion = 0.0;
    float jitter = rand(texCoord) * jitterAmount;

    for(int i = 0; i < sampleDirections; i++) {
        deltaUV = deltaRotationMatrix * deltaUV;

        vec2 sampleDirUV = deltaUV;
        float oldAngle = angleBias;

        for(int j = 0; j < sampleDirections; j++) {
            vec2 sampleUV = texCoord + (jitter + float(j)) * sampleDirUV;
            vec3 sampleVS = getViewPosition(sampleUV);
            vec3 sampleDirVS = (sampleVS - originVS);
            
            float gamma = 1.570796326 - acos(dot(normalVS, normalize(sampleDirVS)));
            
            if (gamma > oldAngle) {
                float value = sin(gamma) - sin(oldAngle);
                
                if(useAttenuation) {
                    float attenuation = clamp(1.0 - pow(length(sampleDirVS) / radiusWS * attenuationScale, 2.0), 0.0, 1.0);
                    occlusion += attenuation * value;
                } else {
                    occlusion += value;
                }
                
                oldAngle = gamma;
            }
        }
    }

    occlusion = 1.0 - (occlusion * intensity) / float(sampleDirections);
    occlusion = clamp(pow(occlusion, 1.0 + intensity), 0.0, 1.0);

    vec3 lumcoeff = vec3(0.299, 0.587, 0.114);
    float lum = dot(color.rgb, lumcoeff) * lumInfluence;

    occlusion = lum + ((1.0 - lum) * occlusion);
    occlusion = mix(occlusion, 1, d);

    fragColor.rgb = color * mix(1.0f, occlusion, power);
    fragColor.a = occlusion;

    if(externalBlur) {
        fragColor.rgb = color;
        fragColor.a = occlusion;
    }
    if(onlyAO) {
        fragColor.rgb = vec3(occlusion);
        fragColor.a = 1.0;
    }

    //fragColor.rgb = vec3(jitter);
}
"""


class HBAO(Filter2D):

    def __init__(self, power=1.0, idx: int = None) -> None:
        cam = logic.getCurrentScene().active_camera
        self.settings = {
            'power': float(power),
            'znear': cam.near,
            'zfar': cam.far,
            'fov': cam.fov
        }
        super().__init__(glsl, idx, {
            'power': self.settings,
            'znear': self.settings,
            'zfar': self.settings,
            'fov': self.settings
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
        self.settings['fov'] = cam.fov

