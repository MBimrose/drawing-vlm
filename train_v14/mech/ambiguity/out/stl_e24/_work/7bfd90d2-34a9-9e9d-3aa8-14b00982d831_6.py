from build123d import *

outer_radius = 30.0
inner_radius = 8.0
collar_length = 20.0
keyway_width = 10.0
keyway_depth = 3.0
set_screw_diameter = 4.0
set_screw_depth = 8.0
set_screw_angle = 30.0
chamfer_size = 1.0
fillet_radius = 1.5
pocket_width = 12.0
pocket_height = 6.0
pocket_depth = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, collar_length))
            l3 = Line(l2@1, (inner_radius, collar_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

keyway_box = Pos(inner_radius - keyway_depth/2, 0, 0) * Box(keyway_depth, collar_length, keyway_width)
solid_body = solid_body - keyway_box

import math
for angle in [set_screw_angle, -set_screw_angle]:
    rad = math.radians(angle)
    x = outer_radius - set_screw_depth/2
    hole = Pos(x * math.cos(rad), x * math.sin(rad), collar_length/2) * Rot(0, 90, angle) * Cylinder(set_screw_diameter/2, set_screw_depth)
    solid_body = solid_body - hole

pocket_box = Pos(outer_radius - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket_box

part = solid_body
part.name = "collar_with_keyway"
export_step(part, "output.step")