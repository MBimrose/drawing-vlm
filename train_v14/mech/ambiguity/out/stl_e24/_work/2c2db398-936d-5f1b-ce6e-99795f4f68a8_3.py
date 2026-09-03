from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
pocket_radius = 12.0
pocket_depth = 4.0
pocket_offset_x = 20.0
pocket_offset_y = 0.0
fillet_radius = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)
pocket = Pos(pocket_offset_x, pocket_offset_y, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_radius, pocket_depth)
solid_body = solid_body - pocket
vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_pocket"
export_step(part, "output.step")