from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
length = 70.0
groove_width = 15.0
groove_depth = 5.0
groove_position = 20.0
chamfer_distance = 2.0
set_screw_diameter = 4.0
set_screw_offset = 10.0
keyway_width = 6.0
keyway_depth = 4.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
groove_radius = outer_radius - groove_depth

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, groove_position))
            l2 = Line(l1@1, (groove_radius, groove_position))
            l3 = Line(l2@1, (groove_radius, groove_position + groove_width))
            l4 = Line(l3@1, (outer_radius, groove_position + groove_width))
            l5 = Line(l4@1, (outer_radius, length))
            l6 = Line(l5@1, (inner_radius, length))
            l7 = Line(l6@1, (inner_radius, 0))
            l8 = Line(l7@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

solid_body = solid_body - Pos(set_screw_offset, 0, length/2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, outer_diameter)

solid_body = solid_body - Pos(inner_radius - keyway_depth/2, 0, length/2) * Box(keyway_depth, keyway_width, length)

part = solid_body
part.name = "grooved_shaft_with_keyway"
export_step(part, "output.step")