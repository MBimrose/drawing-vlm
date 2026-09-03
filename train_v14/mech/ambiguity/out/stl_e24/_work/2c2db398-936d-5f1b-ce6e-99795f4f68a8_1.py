from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
corner_fillet_radius = 2.0
cavity_radius = 12.0
cavity_depth = 4.0
cavity_offset_x = 20.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = solid_body - Pos(cavity_offset_x, 0, plate_thickness/2 - cavity_depth/2) * Cylinder(cavity_radius, cavity_depth)

part = solid_body
part.name = "plate_with_cavity"
export_step(part, "output.step")