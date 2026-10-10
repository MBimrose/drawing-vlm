from build123d import *

outer_radius = 30.0
total_height = 60.0
rib_height = 10.0
rib_thickness = 4.0
rib_position = 45.0
central_hole_diameter = 12.0
counterbore_diameter = 20.0
counterbore_depth = 20.0
set_screw_diameter = 5.0
set_screw_offset = outer_radius - 7.0
set_screw_position = 30.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, rib_position - rib_height / 2))
            l3 = Line(l2 @ 1, (outer_radius + rib_thickness, rib_position - rib_height / 2))
            l4 = Line(l3 @ 1, (outer_radius + rib_thickness, rib_position + rib_height / 2))
            l5 = Line(l4 @ 1, (outer_radius, rib_position + rib_height / 2))
            l6 = Line(l5 @ 1, (outer_radius, total_height))
            l7 = Line(l6 @ 1, (0, total_height))
            l8 = Line(l7 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, total_height)
solid_body = solid_body - Pos(0, 0, counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)
solid_body = solid_body - Pos(set_screw_offset, 0, set_screw_position) * Cylinder(set_screw_diameter / 2, total_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "revolved_ribbed_cylinder"
export_step(part, "output.step")