from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
length = 70.0
shoulder_length = 15.0
shoulder_diameter = 30.0
set_screw_diameter = 4.0
set_screw_offset = 35.0
chamfer_size = 2.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_length = 45.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, shoulder_length))
            l3 = Line(l2 @ 1, (shoulder_radius, shoulder_length))
            l4 = Line(l3 @ 1, (shoulder_radius, length - shoulder_length))
            l5 = Line(l4 @ 1, (outer_radius, length - shoulder_length))
            l6 = Line(l5 @ 1, (outer_radius, length))
            l7 = Line(l6 @ 1, (0, length))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(inner_radius, length)
solid_body = solid_body - Pos(0, 0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, outer_diameter)
solid_body = solid_body - Pos(inner_radius - keyway_depth / 2, 0, length / 2) * Box(keyway_depth, keyway_width, keyway_length)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "stepped_shaft_with_keyway"
export_step(part, "output.step")