from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 5.0
hole_diameter = 5.0
hole_spacing = 10.0
hole_count = 5
fillet_radius = 2.0
rib_height = 4.0
rib_thickness = 4.0
rib_offset = 2.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

rib_length = plate_length - 20.0
rib_y_offset = plate_width / 2 - rib_thickness / 2 - rib_offset

rib_top = Pos(0, rib_y_offset, plate_thickness / 2 + rib_height / 2) * Box(rib_length, rib_thickness, rib_height)
rib_bottom = Pos(0, -rib_y_offset, plate_thickness / 2 + rib_height / 2) * Box(rib_length, rib_thickness, rib_height)
rib_center = Pos(0, 0, plate_thickness / 2 + rib_height / 2) * Box(rib_length, rib_thickness, rib_height)

solid_body = solid_body + rib_top + rib_bottom + rib_center

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter / 2, 20)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")