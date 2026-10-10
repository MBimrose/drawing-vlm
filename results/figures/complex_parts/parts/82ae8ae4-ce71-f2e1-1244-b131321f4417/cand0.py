from build123d import *

outer_diameter = 60.0
length = 60.0
bore_diameter = 12.0
counterbore_diameter = 20.0
counterbore_depth = 15.0
rib_thickness = 4.0
rib_width = 12.0
rib_position = 30.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
bore_radius = bore_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0
rib_outer_radius = outer_radius + rib_thickness

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, rib_position))
            l3 = Line(l2 @ 1, (rib_outer_radius, rib_position))
            l4 = Line(l3 @ 1, (rib_outer_radius, rib_position + rib_width))
            l5 = Line(l4 @ 1, (outer_radius, rib_position + rib_width))
            l6 = Line(l5 @ 1, (outer_radius, length))
            l7 = Line(l6 @ 1, (0, length))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, counterbore_depth / 2) * Cylinder(counterbore_radius, counterbore_depth)
solid_body = solid_body - Pos(0, 0, length / 2) * Cylinder(bore_radius, length)
solid_body = solid_body - Pos(outer_radius - mount_hole_offset, 0, length / 2) * Cylinder(mount_hole_diameter / 2, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_cylinder_with_rib"
export_step(part, "output.step")