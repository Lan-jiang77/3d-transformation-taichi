import taichi as ti
import math

ti.init(arch=ti.cpu)


def get_model_matrix(angle):
    rad = angle * math.pi / 180.0
    c = math.cos(rad)
    s = math.sin(rad)

    return ti.Matrix([
        [c, -s, 0.0, 0.0],
        [s,  c, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])


def get_view_matrix(eye_pos):
    x, y, z = eye_pos
    return ti.Matrix([
        [1.0, 0.0, 0.0, -x],
        [0.0, 1.0, 0.0, -y],
        [0.0, 0.0, 1.0, -z],
        [0.0, 0.0, 0.0, 1.0]
    ])


def get_projection_matrix(eye_fov, aspect_ratio, zNear, zFar):
    fov = eye_fov * math.pi / 180.0

    n = -zNear
    f = -zFar

    t = math.tan(fov / 2.0) * abs(n)
    b = -t
    r = aspect_ratio * t
    l = -r

    persp_to_ortho = ti.Matrix([
        [n,   0.0, 0.0,    0.0],
        [0.0, n,   0.0,    0.0],
        [0.0, 0.0, n + f, -n * f],
        [0.0, 0.0, 1.0,    0.0]
    ])

    ortho_translate = ti.Matrix([
        [1.0, 0.0, 0.0, -(r + l) / 2.0],
        [0.0, 1.0, 0.0, -(t + b) / 2.0],
        [0.0, 0.0, 1.0, -(n + f) / 2.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    ortho_scale = ti.Matrix([
        [2.0 / (r - l), 0.0, 0.0, 0.0],
        [0.0, 2.0 / (t - b), 0.0, 0.0],
        [0.0, 0.0, 2.0 / (n - f), 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ])

    ortho = ortho_scale @ ortho_translate
    return ortho @ persp_to_ortho


def transform_vertex(vertex, mvp):
    v = ti.Vector([vertex[0], vertex[1], vertex[2], 1.0])
    v = mvp @ v
    v = v / v[3]

    x = (v[0] + 1.0) / 2.0
    y = (v[1] + 1.0) / 2.0
    return x, y


def main():
    gui = ti.GUI("3D Transformation (Taichi)", res=(700, 700), background_color=0x000000)

    vertices = [
        [2.0, 0.0, -2.0],
        [0.0, 2.0, -2.0],
        [-2.0, 0.0, -2.0]
    ]

    eye_pos = [0.0, 0.0, 5.0]
    angle = 0.0

    while gui.running:
        for e in gui.get_events(ti.GUI.PRESS):
            if e.key == ti.GUI.ESCAPE:
                gui.running = False

        if gui.is_pressed('a'):
            angle += 1.0
        if gui.is_pressed('d'):
            angle -= 1.0

        model = get_model_matrix(angle)
        view = get_view_matrix(eye_pos)
        projection = get_projection_matrix(
            eye_fov=45.0,
            aspect_ratio=1.0,
            zNear=0.1,
            zFar=50.0
        )

        mvp = projection @ view @ model

        p0 = transform_vertex(vertices[0], mvp)
        p1 = transform_vertex(vertices[1], mvp)
        p2 = transform_vertex(vertices[2], mvp)

        gui.clear(0x000000)
        gui.line(begin=p0, end=p1, radius=2, color=0xFF0000)
        gui.line(begin=p1, end=p2, radius=2, color=0x00FF00)
        gui.line(begin=p2, end=p0, radius=2, color=0x0000FF)

        gui.show()


if __name__ == "__main__":
    main()