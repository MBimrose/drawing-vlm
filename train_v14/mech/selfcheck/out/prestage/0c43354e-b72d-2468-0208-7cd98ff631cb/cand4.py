from build123d import *

outer_length = 80.0
outer_width = 30.0
outer_height = 60.0
wall_thickness = 1.0
rib_thickness = 2.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset = 12.0
chamfer_size = 0.5

solid_body = Box(outer_length, outer_width, outer_height)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[bottom_face])

rib = Box(rib_thickness, outer_width, outer_height - 2 * wall_thickness)
solid_body = solid_body + rib

for i in range(3):
    x = -outer_length / 2 + hole_offset + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, outer_height + 10)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
outer_edges = [e for e in vertical_edges if abs(e.center().X) > outer_length / 2 - 0.1 or abs(e.center().Y) > outer_width / 2 - 0.1]
solid_body = chamfer(outer_edges, chamfer_size)

part = solid_body
part.name = "shelled_box_with_rib"
export_step(part, "output.step")