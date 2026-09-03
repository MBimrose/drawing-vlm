from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_width = 10.0
rib_height = 4.0
blind_hole_diameter = 24.0
blind_hole_depth = 4.0
blind_hole_offset_x = 20.0
blind_hole_offset_y = 0.0
fillet_radius = 2.0

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Box(plate_length - 2 * rib_width, rib_width, rib_height)
rib2 = Box(rib_width, plate_width - 2 * rib_width, rib_height)

solid_body = base + rib1 + rib2

hole = Pos(blind_hole_offset_x, blind_hole_offset_y, plate_thickness/2 - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)
solid_body = solid_body - hole

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_ribs_and_hole"
export_step(part, "output.step")