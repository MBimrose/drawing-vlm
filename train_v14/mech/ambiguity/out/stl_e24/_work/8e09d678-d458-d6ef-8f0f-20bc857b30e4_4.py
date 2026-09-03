from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 2.0
chamfer_size = 1.5
opening_width = 15.0
opening_height = 10.0
opening_offset_z = 5.0
hole_diameter = 3.0
hole_spacing_x = 50.0
hole_spacing_y = 40.0

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

opening_cut = Pos(0, outer_width/2 - wall_thickness/2, opening_offset_z) * Box(opening_width, wall_thickness, opening_height)
solid_body = solid_body - opening_cut

for x, y in [(-hole_spacing_x/2, -hole_spacing_y/2), (hole_spacing_x/2, -hole_spacing_y/2),
             (-hole_spacing_x/2, hole_spacing_y/2), (hole_spacing_x/2, hole_spacing_y/2)]:
    solid_body = solid_body - Pos(x, y, outer_height/2) * Cylinder(hole_diameter/2, outer_height)

rear_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[:2]
solid_body = chamfer(rear_edges, chamfer_size)

part = solid_body
part.name = "shelled_box_with_opening"
export_step(part, "output.step")