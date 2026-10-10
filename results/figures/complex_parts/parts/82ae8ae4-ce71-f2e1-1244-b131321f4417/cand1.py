from build123d import *

outer_radius = 30
inner_radius = 6
rib_thickness = 4
rib_height = 12
rib_base = 30
total_height = 60
counterbore_diameter = 20
counterbore_depth = 15
through_hole_diameter = 5
chamfer_size = 1

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, rib_base))
            l3 = Line(l2 @ 1, (outer_radius + rib_thickness, rib_base))
            l4 = Line(l3 @ 1, (outer_radius + rib_thickness, rib_base + rib_height))
            l5 = Line(l4 @ 1, (outer_radius, rib_base + rib_height))
            l6 = Line(l5 @ 1, (outer_radius, total_height))
            l7 = Line(l6 @ 1, (0, total_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = solid_body - Cylinder(inner_radius, total_height)
solid_body = solid_body - Pos(0, 0, counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - Pos(outer_radius - through_hole_diameter, 0, total_height / 2) * Cylinder(through_hole_diameter / 2, total_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_ribbed_cylinder"
export_step(part, "output.step")