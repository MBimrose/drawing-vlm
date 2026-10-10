from build123d import *

outer_radius = 30.0
inner_radius = 10.0
body_height = 60.0
rib_height = 10.0
rib_thickness = 4.0
rib_position = 35.0
counterbore_diameter = 20.0
counterbore_depth = 15.0
through_hole_diameter = 12.0
mount_hole_diameter = 5.0
mount_hole_offset = 23.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, rib_position))
            l3 = Line(l2 @ 1, (outer_radius + rib_thickness, rib_position))
            l4 = Line(l3 @ 1, (outer_radius + rib_thickness, rib_position + rib_height))
            l5 = Line(l4 @ 1, (outer_radius, rib_position + rib_height))
            l6 = Line(l5 @ 1, (outer_radius, body_height))
            l7 = Line(l6 @ 1, (0, body_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(through_hole_diameter / 2, body_height)
solid_body = solid_body - Pos(0, 0, counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - Pos(mount_hole_offset, 0, body_height / 2) * Cylinder(mount_hole_diameter / 2, body_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_body_with_rib_and_holes"
export_step(part, "output.step")