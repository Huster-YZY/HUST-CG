import math

def generate_sphere(radius, num_segments, output_file):
    vertices = []
    faces = []

    for i in range(num_segments + 1):
        for j in range(num_segments + 1):
            theta = 2 * math.pi * j / num_segments
            phi = math.pi * i / num_segments

            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)

            vertices.append((x, y, z))

    for i in range(num_segments):
        for j in range(num_segments):
            v1 = i * (num_segments + 1) + j
            v2 = v1 + 1
            v3 = v1 + num_segments + 2
            v4 = v1 + num_segments + 1

            faces.append((v1, v2, v3))
            faces.append((v1, v3, v4))

    with open(output_file, 'w') as f:
        for v in vertices:
            f.write(f'v {v[0]} {v[1]} {v[2]}\n')

        for face in faces:
            f.write(f'f {face[0]+1} {face[1]+1} {face[2]+1}\n')

# Generate a sphere with radius 1 and 100 segments
generate_sphere(1, 150, 'sphere.obj')