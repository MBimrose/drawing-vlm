from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
flange_extension = 30.0
flange_width = 15.0
hole_diameter = 12.0
chamfer_distance = 1.0
rib_height = 4.0
rib_width = 6.0
rib_spacing = 12.0

base_plate = Box(plate_length, plate_width, plate_thickness)
flange = Pos(plate_length/2 + flange_extension/2, 0, 0) * Box(flange_extension, flange_width, plate_thickness)
result = base_plate + flange
result = chamfer(result.edges(), chamfer_distance)
result = result - Pos(plate_length/2 + flange_extension, 0, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib_count = int((plate_length - 2 * rib_spacing) // (rib_width + rib_spacing))
for i in range(rib_count):
    x_offset = -plate_length/2 + rib_spacing + i * (rib_width + rib_spacing) + rib_width/2
    rib = Pos(x_offset, 0, 0) * Box(rib_width, plate_width - 2 * rib_spacing, rib_height)
    result = result + rib

part = result
part.name = "plate_with_flange_and_ribs"
export_step(part, "output.step")