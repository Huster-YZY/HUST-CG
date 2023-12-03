import taichi as ti
import trimesh
import numpy as np
from PIL import Image

# ti.init(ti.cuda)
ti.init(ti.metal)

VERTEX_NUMBER=22352
FACE_NUMBER=45000
filename='./assets/sphere.obj'
WIDTH=1024
HEIGHT=2048
TEX_RESOLUTION=(WIDTH,HEIGHT)

ball_center=ti.Vector.field(3,dtype=float,shape=(1,))
ball_center[0]=[.0,.0,.0]
earth_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
moon_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
sun_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)

earth_colors=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
tex=ti.Vector.field(3,dtype=int,shape=TEX_RESOLUTION)
uv_coords=ti.Vector.field(2,dtype=float,shape=VERTEX_NUMBER)
indices=ti.field(ti.i32,shape=3*FACE_NUMBER)

@ti.kernel
def computeUV():
    for i in ti.grouped(earth_vertices):
        x,y,z=earth_vertices[i]
        l=ti.math.sqrt(x**2+y**2+z**2)
        x,y,z=earth_vertices[i]/l
        azimuthal_angle=ti.math.atan2(y,x)
        if azimuthal_angle<0:
            azimuthal_angle+=2*ti.math.pi
        polar_angle=ti.math.acos(z)
        u=azimuthal_angle/(2*ti.math.pi)
        v=polar_angle/ti.math.pi
        uv_coords[i]=ti.Vector((u,v))

def loadObjects():
    'Load the 3D model'
    mesh=trimesh.load(filename,force='mesh')
    earth_vertices.from_numpy(mesh.vertices.astype('float32'))
    np_indices=mesh.faces.astype('int32')
    np_indices=np_indices.reshape(-1)
    indices.from_numpy(np_indices)


@ti.kernel
def render_earth():
    for i in ti.grouped(earth_colors):
        earth_colors[i]=tex[int(uv_coords[i][1]*WIDTH),int(uv_coords[i][0]*HEIGHT)]/255.0

def texture_mapping():
    earth=Image.open('./assets/textures/earth.jpg').convert('RGB')
    print(np.array(earth).shape)
    tex.from_numpy(np.array(earth))
    render_earth()

def main():
    loadObjects()
    computeUV()
    texture_mapping()
    window=ti.ui.Window("Sun Earth Moon",(1024,1024),vsync=True)
    canvas=window.get_canvas()
    
    scene=ti.ui.Scene()
    camera=ti.ui.Camera()
    camera.position(0,5,0)
    
    while window.running:
        scene.point_light(pos=(0,1,0),color=(1,1,1))
        scene.ambient_light((0.5,0.5,0.5))
        camera.track_user_inputs(window,movement_speed=0.05,hold_key=ti.ui.LMB)

        scene.set_camera(camera)
        # scene.particles(centers=ball_center,radius=0.1,color=(1.0,0.0,0.0))
        scene.mesh(vertices=earth_vertices,indices=indices,color=(1.0,.0,.0),per_vertex_color=earth_colors)


        canvas.scene(scene)
        canvas.set_background_color((0.,0.,0.))
        window.show()


if __name__=="__main__":
    main()