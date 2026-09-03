from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_width = 20.0
slot_length = 40.0
hole_diameter = 4.0
hole_spacing = 40.0
chamfer_size = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body - Box(slot_width, slot_length, plate_thickness)

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_slot_and_holes"
export_step(part, "output.step")