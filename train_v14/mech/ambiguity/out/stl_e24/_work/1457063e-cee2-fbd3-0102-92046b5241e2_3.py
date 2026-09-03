from build123d import *

outer_length = 100.0
outer_width = 60.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 5.0
rib_height = outer_height - 2 * wall_thickness
hole_diameter = 7.0
hole_count = 7
chamfer_size = 0.8

solid_body = Box(outer_length, outer_width, outer_height)
solid_body = offset(solid_body, amount=-wall_thickness)

rib = Box(rib_thickness, outer_width - 2 * wall_thickness, rib_height)
solid_body = solid_body + Pos(outer_length/2 - rib_thickness/2, 0, 0) * rib
solid_body = solid_body + Pos(-outer_length/2 + rib_thickness/2, 0, 0) * rib

pocket = Box(outer_length - 2 * wall_thickness, outer_width - 2 * wall_thickness, wall_thickness * 2)
solid_body = solid_body - Pos(0, 0, outer_height/2 - wall_thickness) * pocket

hole_spacing = (outer_length - 2 * wall_thickness) / (hole_count - 1)
for i in range(hole_count):
    x = -outer_length/2 + wall_thickness + i * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, outer_height)

left_face = solid_body.faces().sort_by(Axis.X)[0]
solid_body = chamfer(left_face.edges(), chamfer_size)

part = solid_body
part.name = "shelled_box_with_ribs"
export_step(part, "output.step")