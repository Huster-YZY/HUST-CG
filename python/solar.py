import taichi as ti
import trimesh
ti.init(ti.cuda)

VERTEX_NUMBER=5958
FACE_NUMBER=11904
filename='./assets/ball.obj'
ball_center=ti.Vector.field(3,dtype=float,shape=(1,))
ball_center[0]=[.0,.0,.0]
earth_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
moon_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
sun_vertices=ti.Vector.field(3,dtype=float,shape=VERTEX_NUMBER)
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
    earth_vertices.from_numpy(mesh.vertices)
    np_indices=mesh.faces.astype('int32')
    np_indices=np_indices.reshape(-1)
    indices.from_numpy(np_indices)

def main():
    loadObjects()
    computeUV()
    window=ti.ui.Window("Sun Earth Moon",(1024,1024),vsync=True)
    canvas=window.get_canvas()
    
    scene=ti.ui.Scene()
    camera=ti.ui.Camera()
    camera.position(0,0,5)
    
    while window.running:
        scene.point_light(pos=(0,1,0),color=(1,1,1))
        scene.ambient_light((0.5,0.5,0.5))
        camera.track_user_inputs(window,movement_speed=0.05,hold_key=ti.ui.LMB)

        scene.set_camera(camera)
        # scene.particles(centers=ball_center,radius=0.1,color=(1.0,0.0,0.0))
        scene.mesh(vertices=earth_vertices,indices=indices,color=(1.0,.0,.0))


        canvas.scene(scene)
        canvas.set_background_color((0.,0.,0.))
        window.show()


if __name__=="__main__":
    main()