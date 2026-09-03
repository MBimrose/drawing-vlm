from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_thickness = 8.0
wall_thickness = 2.0
corner_fillet_radius = 5.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_y = 15.0

solid_body = Box(outer_length, outer_width, outer_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, corner_fillet_radius)
pocket = Pos(0, 0, outer_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket
for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, hole_offset_y)]:
    hole = Pos(x, y, 0) * Cylinder(hole_diameter/2, outer_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "shelled_plate_with_pocket_and_holes"
export_step(part, "output.step")