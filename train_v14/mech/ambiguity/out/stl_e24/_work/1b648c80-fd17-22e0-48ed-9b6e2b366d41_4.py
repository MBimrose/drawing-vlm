from build123d import *

outer_diameter = 40
inner_diameter = 20
length = 70
shoulder_length = 15
shoulder_diameter = 30
entry_chamfer = 2
set_screw_diameter = 4
set_screw_offset = 35
keyway_width = 6
keyway_depth = 5
outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, shoulder_length))
            l2 = Line(l1@1, (shoulder_radius, shoulder_length))
            l3 = Line(l2@1, (shoulder_radius, shoulder_length + 10))
            l4 = Line(l3@1, (outer_radius, shoulder_length + 10))
            l5 = Line(l4@1, (outer_radius, length))
            l6 = Line(l5@1, (inner_radius, length))
            l7 = Line(l6@1, (inner_radius, 0))
            l8 = Line(l7@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), entry_chamfer)

set_screw_hole = Pos(0, 0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, outer_diameter)
solid_body = solid_body - set_screw_hole

keyway = Pos(inner_radius - keyway_depth / 2, 0, length / 2) * Box(keyway_depth, keyway_width, length)
solid_body = solid_body - keyway

part = solid_body
part.name = "stepped_shaft_with_keyway"
export_step(part, "output.step")