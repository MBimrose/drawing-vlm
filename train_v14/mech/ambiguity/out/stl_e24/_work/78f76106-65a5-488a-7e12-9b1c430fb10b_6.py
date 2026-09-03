from build123d import *

arm_length = 80.0
base_radius = 15.0
tip_radius = 5.0
shoulder_length = 20.0
shoulder_radius = base_radius
hole_diameter = 12.0
fillet_radius = 10.0
pocket_width = 20.0
pocket_depth = 6.0
pocket_spacing = 15.0
pocket_count = int((arm_length - shoulder_length) / pocket_spacing)

with BuildPart() as p:
    with BuildSketch(Plane.XY) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (0, base_radius))
            l2 = Line(l1 @ 1, (arm_length, tip_radius))
            l3 = Line(l2 @ 1, (arm_length, 0))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.X)

solid_body = p.part

shoulder = Pos(arm_length + shoulder_length / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(shoulder_radius, shoulder_length)
solid_body = solid_body + shoulder

hole = Pos(arm_length / 2, 0, 0) * Cylinder(hole_diameter / 2, arm_length + shoulder_length + 20)
solid_body = solid_body - hole

for i in range(pocket_count):
    x_pos = arm_length / 2 + (i - (pocket_count - 1) / 2) * pocket_spacing
    pocket = Pos(x_pos, 0, 0) * Box(pocket_width, pocket_depth, base_radius + 2)
    solid_body = solid_body - pocket

fillet_sphere = Pos(0, 0, base_radius - fillet_radius) * Sphere(fillet_radius)
solid_body = solid_body + fillet_sphere

part = solid_body
part.name = "arm_with_pockets"
export_step(part, "output.step")