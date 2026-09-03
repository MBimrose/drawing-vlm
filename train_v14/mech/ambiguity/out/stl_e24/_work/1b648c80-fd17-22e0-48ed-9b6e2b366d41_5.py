from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
length = 70.0
grip_start = 10.0
grip_length = 12.0
grip_diameter = 30.0
set_screw_diameter = 4.0
set_screw_position = 35.0
keyway_width = 6.0
keyway_depth = 5.0
chamfer_distance = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
grip_radius = grip_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, grip_start))
            l2 = Line(l1@1, (grip_radius, grip_start))
            l3 = Line(l2@1, (grip_radius, grip_start + grip_length))
            l4 = Line(l3@1, (outer_radius, grip_start + grip_length))
            l5 = Line(l4@1, (outer_radius, length))
            l6 = Line(l5@1, (inner_radius, length))
            l7 = Line(l6@1, (inner_radius, 0))
            l8 = Line(l7@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

set_screw_hole = Pos(0, 0, set_screw_position) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, outer_diameter + 2.0)
solid_body = solid_body - set_screw_hole

keyway = Pos(inner_radius - keyway_depth / 2.0, 0, length / 2.0) * Box(keyway_depth, keyway_width, length)
solid_body = solid_body - keyway

part = solid_body
part.name = "revolved_shaft_with_grip"
export_step(part, "output.step")