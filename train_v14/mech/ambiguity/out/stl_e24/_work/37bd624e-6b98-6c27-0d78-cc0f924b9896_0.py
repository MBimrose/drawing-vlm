from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = 4.0
rib_spacing = 12.0
hole_diameter = 3.0
hole_spacing_x = 30.0
hole_spacing_y = 20.0
chamfer_size = 0.2
notch_width = 10.0
notch_height = outer_height - 2 * wall_thickness
notch_offset = 5.0

solid_body = Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

inner_length = outer_length - 2 * wall_thickness
rib_count = int((outer_width - 2 * wall_thickness) // rib_spacing)
for i in range(rib_count):
    y_pos = -outer_width/2 + wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(0, y_pos, wall_thickness + rib_height/2) * Box(inner_length, rib_thickness, rib_height)
    solid_body = solid_body + rib

for x in [-hole_spacing_x/2, hole_spacing_x/2]:
    for y in [-hole_spacing_y/2, hole_spacing_y/2]:
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, outer_height)

notch = Pos(outer_length/2 - wall_thickness/2, notch_offset, 0) * Box(wall_thickness, notch_width, notch_height)
solid_body = solid_body - notch

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "hollow_box_with_ribs"
export_step(part, "output.step")