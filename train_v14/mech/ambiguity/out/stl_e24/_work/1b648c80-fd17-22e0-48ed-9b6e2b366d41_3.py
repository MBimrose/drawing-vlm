from build123d import *

outer_radius = 20.0
inner_radius = 10.0
height = 70.0
step_height = 10.0
step_radius = 15.0
keyway_width = 5.0
keyway_depth = 8.0
keyway_position = 12.0
set_screw_diameter = 4.0
set_screw_offset = 35.0
chamfer_size = 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, step_height))
            l3 = Line(l2 @ 1, (step_radius, step_height))
            l4 = Line(l3 @ 1, (step_radius, step_height + 5))
            l5 = Line(l4 @ 1, (outer_radius, step_height + 5))
            l6 = Line(l5 @ 1, (outer_radius, height))
            l7 = Line(l6 @ 1, (0, height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, height / 2) * Cylinder(inner_radius, height)
solid_body = solid_body - Pos(inner_radius, 0, keyway_position + height / 2) * Box(keyway_width, keyway_depth, height)
solid_body = solid_body - Pos(outer_radius, 0, set_screw_offset) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2, outer_radius * 2)
bottom_edges = solid_body.edges().sort_by(Axis.Z)[:1]
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "stepped_shaft_with_keyway"
export_step(part, "output.step")