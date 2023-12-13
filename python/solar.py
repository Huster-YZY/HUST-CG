import trimesh
import numpy as np
import taichi as ti
from PIL import Image

#Detect Graphics Hardware
arch=ti.cpu
if ti._lib.core.with_metal():
    arch=ti.metal
elif ti._lib.core.with_vulkan():
    arch=ti.vulkan
elif ti._lib.core.with_cuda():
    arch=ti.cuda

ti.init(arch=arch)

#Parameter Setting 
dt=0.001
VERTEX_NUMBER=22352
FACE_NUMBER=45000
filename='./assets/sphere.obj'
WIDTH=1024
HEIGHT=2048
TEX_RESOLUTION=(WIDTH,HEIGHT)
earth_to_sun=5 #distance
moon_to_earth=0.5

#Memory Allocation
K=ti.field(dtype=float,shape=())
sphere_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
earth_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
moon_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
sun_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)

earth_normals=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
moon_normals=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)

earth_colors=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
sun_colors=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
moon_colors=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)

earth_x=ti.Vector.field(3,dtype=float,shape=())
earth_v=ti.Vector.field(3,dtype=float,shape=())
earth_angular=ti.field(dtype=float,shape=())
earth_angular_velocity=2.0

moon_x=ti.Vector.field(3,dtype=float,shape=())
moon_v=ti.Vector.field(3,dtype=float,shape=())
moon_rotation_angular=ti.field(dtype=float,shape=())
moon_rotation_v=1.5
moon_revolution_angular=ti.field(dtype=float,shape=())
moon_revolution_v=1.5

tex=ti.Vector.field(3,dtype=int,shape=TEX_RESOLUTION)
uv_coords=ti.Vector.field(2,dtype=float,shape=VERTEX_NUMBER)
indices=ti.field(ti.i32,shape=3*FACE_NUMBER)

@ti.kernel
def computeUV():
    '''
    Compute Sphere UV coordinates.
    '''
    for i in ti.grouped(sphere_vertices):
        x,y,z=sphere_vertices[i]
        l=ti.math.sqrt(x**2+y**2+z**2)
        x,y,z=sphere_vertices[i]/l
        azimuthal_angle=ti.math.atan2(y,x)
        if azimuthal_angle<0:
            azimuthal_angle+=2*ti.math.pi
        polar_angle=ti.math.acos(z)
        u=azimuthal_angle/(2*ti.math.pi)
        v=polar_angle/ti.math.pi
        uv_coords[i]=ti.Vector((u,v))

def loadObjects():
    '''
    Load 3D model and Send geometry data to GPU (if applicable).
    '''
    mesh=trimesh.load(filename,force='mesh')
    sphere_vertices.from_numpy(mesh.vertices.astype('float32'))
    np_indices=mesh.faces.astype('int32')
    np_indices=np_indices.reshape(-1)
    indices.from_numpy(np_indices)


@ti.kernel
def render_earth():
    '''
    Assign vertex color according to UV coordinates.
    '''
    for i in ti.grouped(earth_colors):
        earth_colors[i]=tex[int(uv_coords[i][1]*WIDTH),int(uv_coords[i][0]*HEIGHT)]/255.0

@ti.kernel
def render_sun():
    for i in ti.grouped(earth_colors):
        sun_colors[i]=tex[int(uv_coords[i][1]*WIDTH),int(uv_coords[i][0]*HEIGHT)]/255.0

@ti.kernel
def render_moon():
    for i in ti.grouped(earth_colors):
        moon_colors[i]=tex[int(uv_coords[i][1]*WIDTH),int(uv_coords[i][0]*HEIGHT)]/255.0

def texture_mapping():
    #Load Texture Image
    earth=Image.open('./assets/textures/earth.jpg').convert('RGB')
    #Send Texture to GPU (if applicable)
    tex.from_numpy(np.array(earth))
    #Assign the vertex color
    render_earth()

    sun=Image.open('./assets/textures/sun.jpg').convert('RGB')
    tex.from_numpy(np.array(sun))
    render_sun()

    moon=Image.open('./assets/textures/moon.jpg')
    tex.from_numpy(np.array(moon))
    render_moon()

def render(scene):
    '''
    Draw the textured meshes.
    '''
    scene.mesh(vertices=sun_vertices,indices=indices,per_vertex_color=sun_colors)
    scene.mesh(vertices=earth_vertices,indices=indices,per_vertex_color=earth_colors,normals=earth_normals)
    scene.mesh(vertices=moon_vertices,indices=indices,per_vertex_color=moon_colors,normals=moon_normals)

@ti.func
def get_rotation_matrix(angular,axis):
    '''
    Generate Rotation Matrix according to the given angular and rotation axis.\n
    angular: 0~360\n
    axis:
    0: x-axis
    1: y-axis
    2: z-axis
    '''
    theta=ti.math.pi*angular/180.0
    ret=ti.Matrix([
            [1.0,.0,.0],
            [.0,ti.cos(theta),-ti.sin(theta)],
            [.0,ti.sin(theta),ti.cos(theta)]])
    if axis==1:
        ret=ti.Matrix([
            [ti.cos(theta),.0,ti.sin(theta)],
            [.0,1.0,.0],
            [-ti.sin(theta),.0,ti.cos(theta)]])
    elif axis==2:
       ret=ti.Matrix([
            [ti.cos(theta),-ti.sin(theta),.0],
            [ti.sin(theta),ti.cos(theta),.0],
            [.0,.0,1.0]])
    return ret
    
@ti.kernel
def transformation():
    "Geometry Transformation"
    sun_scale=2.0
    earth_scale=0.4
    moon_scale=0.1
    earth_rot=get_rotation_matrix(earth_angular[None],2)
    moon_rot=get_rotation_matrix(moon_rotation_angular[None],0)
    moon_rev=get_rotation_matrix(moon_revolution_angular[None],0)
    for i in ti.grouped(sphere_vertices):
        sun_vertices[i]=sphere_vertices[i]*sun_scale
        earth_vertices[i]=earth_rot@sphere_vertices[i]*earth_scale+earth_x[None]
        earth_normals[i]=earth_vertices[i]-earth_x[None]
        moon_vertices[i]=moon_rev@(moon_rot@sphere_vertices[i]*moon_scale+ti.Vector([.0,moon_to_earth,.0]))+earth_x[None]
        moon_normals[i]-=moon_rev@ti.Vector([.0,moon_to_earth,.0])+earth_x[None]
    

@ti.func
def gravity(k,pos,center):
    r=pos-center
    return -k*r/r.norm()**3

@ti.kernel
def substep():
    earth_v[None]+=dt*gravity(k=K[None],pos=earth_x[None],center=ti.Vector((.0,.0,.0)))
    earth_x[None]+=dt*earth_v[None]

def check_field_upperbound(field,upper_bound):
    if field[None]>upper_bound:
        field[None]-=upper_bound

def step():
    '''
    Simulation Step.
    '''
    #Explicit Integration
    for _ in range(100):
        substep()
    
    #update rotation angular
    earth_angular[None]+=earth_angular_velocity
    moon_rotation_angular[None]+=moon_rotation_v
    moon_revolution_angular[None]+=moon_revolution_v

    #check numerical boundary
    check_field_upperbound(earth_angular,360)
    check_field_upperbound(moon_rotation_angular,360)
    check_field_upperbound(moon_revolution_angular,360)

    #Geometry Transformation
    transformation()

def init():
    '''
    Initialize parameters, velocities and positions.
    '''
    K[None]=4.0
    ox,oy=0.6,0.8
    earth_v[None]=(-oy,ox,0)
    moon_v[None]=(0,-oy,ox)
    earth_v[None]*=10/earth_to_sun**1.5
    earth_x[None]=(ox*earth_to_sun,oy*earth_to_sun,0)
    

def main():
    #parameter used to record the screen
    result_dir = "../frames"
    video_manager = ti.tools.VideoManager(output_dir=result_dir,
                                        framerate=60,
                                        automatic_build=True)
    save_screen=False
    
    init()
    loadObjects()
    computeUV()
    texture_mapping()

    #Construct a window
    window=ti.ui.Window("Sun Earth Moon",(1024,1024),vsync=True)
    canvas=window.get_canvas()
    gui=window.get_gui()
    scene=ti.ui.Scene()

    #Set up camera
    camera=ti.ui.Camera()
    camera.position(10,10,10)
    camera.lookat(0,0,0)
    camera.up(0,0,1)
    
    #Rendering Loop
    while window.running:
        scene.point_light(pos=(0,0,0),color=(1,1,1))
        scene.ambient_light((0.3,0.3,0.3))
        camera.track_user_inputs(window,movement_speed=0.05,hold_key=ti.ui.LMB)

        scene.set_camera(camera)
        step()#Simulation
        render(scene)#Draw meshes in scene

        canvas.scene(scene)
        canvas.set_background_color((0.,0.,0.))

        #detect keyboard events
        for e in window.get_events(ti.ui.PRESS):
            if e.key =='c':
                init()
            elif e.key=='j':
                K[None]+=1.0
            elif e.key=='k':
                if K[None]>.0:
                    K[None]-=1.0
        
        #record the screen
        if save_screen:
            video_manager.write_frame(window.get_image_buffer_as_numpy())

        #sub window used to display hints
        with gui.sub_window("Gravity", 0.01, 0.01, 0.2, 0.1) as w:
            w.text("Press wasdqe and mouse to move.")
            w.text("Press c: Reset Earth's Position.")
            w.text("Press j: Increase Gravity.")
            w.text("Press k: Reduce Gravity.")
            w.text(f"Current Degree of Gravity:{K[None]:.2f}")

        #update screen
        window.show()


if __name__=="__main__":
    main()