import bpy
import gpu
# from gpu_extras.batch import batch_for_shader
from mathutils import Matrix
from mathutils import Vector
from random import uniform, gauss, random
from uplogic import utils
import bge
from uplogic.events import schedule
import time


def batch_for_shader(shader, type, content, *, indices=None):
    """
    Return a batch already configured and compatible with the shader.

    :arg shader: shader for which a compatible format will be computed.
    :type shader: :class:`gpu.types.GPUShader`
    :arg type: "'POINTS', 'LINES', 'TRIS' or 'LINES_ADJ'".
    :type type: str
    :arg content: Maps the name of the shader attribute with the data to fill the vertex buffer.
    :type content: dict
    :return: compatible batch
    :rtype: :class:`gpu.types.GPUBatch`
    """
    from gpu.types import (
        GPUBatch,
        GPUIndexBuf,
        GPUVertBuf,
        GPUVertFormat,
    )

    def recommended_comp_type(attr_type):
        if attr_type in {'FLOAT', 'VEC2', 'VEC3', 'VEC4', 'MAT3', 'MAT4'}:
            return 'F32'
        if attr_type in {'UINT', 'UVEC2', 'UVEC3', 'UVEC4'}:
            return 'U32'
        # `attr_type` in {'INT', 'IVEC2', 'IVEC3', 'IVEC4', 'BOOL'}.
        return 'I32'

    def recommended_attr_len(attr_name):
        attr_len = 1
        try:
            item = content[attr_name][0]
            while True:
                attr_len *= len(item)
                item = item[0]
        except (TypeError, IndexError):
            pass
        return attr_len

    def recommended_fetch_mode(comp_type):
        if comp_type == 'F32':
            return 'FLOAT'
        return 'INT'

    for data in content.values():
        vbo_len = len(data)
        break
    else:
        raise ValueError("Empty 'content'")

    vbo_format = GPUVertFormat()
    attrs_info = shader.attrs_info_get()
    for name, attr_type in attrs_info:
        comp_type = recommended_comp_type(attr_type)
        attr_len = recommended_attr_len(name)
        vbo_format.attr_add(id=name, comp_type=comp_type, len=attr_len, fetch_mode=recommended_fetch_mode(comp_type))

    vbo = GPUVertBuf(vbo_format, vbo_len)

    for id, data in content.items():
        if len(data) != vbo_len:
            raise ValueError("Length mismatch for 'content' values")
        # print(id, data)
        vbo.attr_fill(id, data)

    if indices is None:
        return GPUBatch(type=type, buf=vbo)
    else:
        ibo = GPUIndexBuf(type=type, seq=indices)
        return GPUBatch(type=type, buf=vbo, elem=ibo)


class Particle:
    
    def __init__(self, system):
        self.system = system

        vert_out = gpu.types.GPUStageInterfaceInfo("my_interface")
        vert_out.smooth('VEC3', "pos")

        self.vertex_shader = """
        
        in vec3 position;
        
        uniform mat4 viewProjectionMatrix;
        uniform vec3 particle_transform;

        out vec3 pos;

        void main()
        {
            vec4 tpos = vec4(particle_transform + position, 1.0f);
            gl_Position = viewProjectionMatrix * tpos;
        }
        """

        self.fragment_shader = """
        out vec4 fragColor;

        void main()
        {
            fragColor = vec4(0.7);
        }
        """

        self.shader = gpu.types.GPUShader(self.vertex_shader, self.fragment_shader)
        self.shader.bind()

        # self.shader = gpu.shader.create_from_info(shader_info)
        # del vert_out
        # del shader_info

        scale = uniform(system.size - system.size_random, system.size + system.size_random) * .5
        self.life_random = uniform(-system.life, system.life)
        
        self.change_velocity()
        self.velocity = self.target_velocity
        # self.velocity = Vector((
        #     uniform(system.velocity[0] - system.velocity_random[0], system.velocity[0] + system.velocity_random[0]),
        #     uniform(system.velocity[1] - system.velocity_random[1], system.velocity[1] + system.velocity_random[1]),
        #     uniform(system.velocity[2] - system.velocity_random[2], system.velocity[2] + system.velocity_random[2])
        # ))

        self.init_pos = self.system.location + Vector((
            uniform(system.start_pos[0] - system.start_pos_random[0], system.start_pos[0] + system.start_pos_random[0]),
            uniform(system.start_pos[1] - system.start_pos_random[1], system.start_pos[1] + system.start_pos_random[1]),
            uniform(system.start_pos[2] - system.start_pos_random[2], system.start_pos[2] + system.start_pos_random[2])
        ))

        coords = [
            # Vector((scale, scale, scale)),
            # Vector((scale, -scale, -scale)),
            # Vector((-scale, scale, scale)),
            # Vector((-scale, scale, -scale)),
            # Vector((scale, scale, scale)),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale))),
            Vector((uniform(-scale, scale), uniform(-scale, scale), uniform(-scale, scale)))
        ]
        self.batch = batch_for_shader(self.shader, 'TRI_FAN', {'position': coords})
        self.pos = self.init_pos.copy()
        self.life = time.time()
        delay = uniform(0, system.life + self.life_random)
        self.stopped = True
        self.started = False
        self.spawn_chance = random()
        schedule(self.start, delay)

    def start(self):
        system = self.system
        if self.spawn_chance > system.emission_rate:
            return
        self.stopped = False
        self.started = True
        self.life = time.time()
        if system.use_gauss:
            self.init_pos = self.system.location + Vector((
                gauss(system.start_pos[0], system.start_pos_random[0] * .33),
                gauss(system.start_pos[1], system.start_pos_random[1] * .33),
                gauss(system.start_pos[2], system.start_pos_random[2] * .33)
            ))
        else:
            self.init_pos = self.system.location + Vector((
                uniform(system.start_pos[0] - system.start_pos_random[0], system.start_pos[0] + system.start_pos_random[0]),
                uniform(system.start_pos[1] - system.start_pos_random[1], system.start_pos[1] + system.start_pos_random[1]),
                uniform(system.start_pos[2] - system.start_pos_random[2], system.start_pos[2] + system.start_pos_random[2])
            ))
        self.life_random = uniform(-system.life, system.life)
        self.pos = self.init_pos.copy()

    def change_velocity(self):
        sys = self.system
        self.target_velocity = Vector((
            uniform(sys.velocity[0] - sys.velocity_random[0], sys.velocity[0] + sys.velocity_random[0]),
            uniform(sys.velocity[1] - sys.velocity_random[1], sys.velocity[1] + sys.velocity_random[1]),
            uniform(sys.velocity[2] - sys.velocity_random[2], sys.velocity[2] + sys.velocity_random[2])
        ))
        schedule(self.change_velocity, uniform(0, 1))

    def check_visible(self):
        if not self.started:
            return
        sys = self.system
        self.pos += self.velocity
        # self.pos += self.calc_gravity()
        # print(self.pos)
        point = sys.cam.rayCast(sys.cam.worldPosition, self.pos)[0]
        # point = utils.raycast(sys.cam, self.pos, sys.cam.worldPosition, visualize=True).point
        if not point:
            self.draw()
    
    def calc_gravity(self):
        t = time.time() - self.life
        half: float = self.system.gravity * (.5 * t * t)
        vel = self.velocity * t
        return half + vel + self.pos

    def update(self):
        if self.stopped:
            return
        sys = self.system
        self.check_visible()
        self.velocity = self.velocity.lerp(self.target_velocity, .01)
        dat = sys.cam.rayCast(self.pos + self.velocity, self.pos)
        if dat[0]:
            self.pos = dat[1] + dat[2] * .01
            self.end()
        elif sys.time - self.life > sys.life + self.life_random:
            self.end()
    
    def end(self):
        self.stopped = True
        self.start()

    def draw(self):
        gpu.state.depth_test_set('ALWAYS')  # NONE, ALWAYS, GREATER and GREATER_EQUAL works, 
        gpu.state.depth_mask_set(True)
        matrix = bpy.context.region_data.perspective_matrix
        self.shader.uniform_float("viewProjectionMatrix", matrix)
        trans = self.pos
        self.shader.uniform_float("particle_transform", trans)
        self.batch.draw(self.shader)
        gpu.state.depth_mask_set(False)


class ParticleSystem:
    
    def __init__(
        self,
        amount=1000,
        life=10,
        life_random=0,
        start_pos=Vector((0, 0, 0)),
        start_pos_random=Vector((0, 0, 0)),
        size=.5,
        size_random=0.0,
        velocity=Vector((0, 0, 0)),
        velocity_random=Vector((0, 0, 0)),
        gravity=Vector((0, 0, -9.8)),
        location=Vector((0, 0, 0)),
        use_gauss=False,
        exclude_occlusion_mask=32768
    ):
        self.life = life
        self.life_random = life_random
        self.emission_rate = 1.0
        self.exclude_occlusion = 65535 - exclude_occlusion_mask
        self.particles = []
        self.start_pos = Vector(start_pos)
        self.start_pos_random = Vector(start_pos_random)
        self.size = size
        self.use_gauss = use_gauss
        self.size_random = size_random
        self.velocity = Vector(velocity)
        self.velocity_random = Vector(velocity_random)
        self.gravity = gravity

        self.location = Vector(location)
        
        self.time = time.time()
        
        for x in range(amount):
            self.particles.append(Particle(self))

        bge.logic.getCurrentScene().post_draw.append(self.update)
    
    def update(self):
        self.cam = bge.logic.getCurrentScene().active_camera
        self.time = time.time()
        for p in self.particles:
            if p.stopped:
                p.start()
            p.check_visible() if p.stopped else p.update()

