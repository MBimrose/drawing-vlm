from build123d import *

outer_radius = 20.0
inner_radius = 10.0
shoulder_radius = 15.0
shoulder_height = 10.0
total_height = 70.0
keyway_width = 6.0
keyway_depth = 5.0
keyway_start = 30.0
keyway_end = 55.0
chamfer_dist = 2.0
hole_diameter = 4.0
hole_offset = 12.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, shoulder_height))
            l2 = Line(l1 @ 1, (shoulder_radius, shoulder_height))
            l3 = Line(l2 @ 1, (shoulder_radius, total_height - keyway_end))
            l4 = Line(l3 @ 1, (outer_radius, total_height - keyway_end))
            l5 = Line(l4 @ 1, (outer_radius, total_height))
            l6 = Line(l5 @ 1, (inner_radius, total_height))
            l7 = Line(l6 @ 1, (inner_radius, 0))
            l8 = Line(l7 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

keyway_box = Pos(inner_radius - keyway_depth / 2, 0, (keyway_start + keyway_end) / 2) * Box(keyway_depth, keyway_width, keyway_end - keyway_start)
solid_body = solid_body - keyway_box

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_dist)

hole_cyl = Pos(outer_radius, 0, total_height / 2) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, total_height)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "stepped_shaft_with_keyway"
export_step(part, "output.step")