from build123d import *

base_radius = 5.0
arm_length = 30.0
arm_width = 10.0
loft_height = 45.0
hole_diameter = 5.0
hole_spacing = 15.0
hole_count = 3

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(loft_height)) as s2:
        with BuildLine() as bl:
            l1 = Line((0, 0), (arm_length, 0))
            l2 = Line(l1 @ 1, (arm_length, arm_width))
            l3 = Line(l2 @ 1, (0, arm_width))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    loft()

solid_body = p.part

for i in range(hole_count):
    x = i * hole_spacing
    z = loft_height / 2
    hole = Pos(x, arm_width / 2, z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, arm_width + 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "lofted_arm_with_holes"
export_step(part, "output.step")