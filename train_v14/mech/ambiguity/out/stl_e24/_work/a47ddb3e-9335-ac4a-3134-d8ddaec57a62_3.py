from build123d import *

plate_width = 60.0
plate_height = 40.0
plate_thickness = 5.0
rib_width = 40.0
rib_height = 8.0
rib_thickness = 3.0
hole_diameter = 5.0
hole_offset_x = 0.0
hole_offset_y = 12.0
slot_width = 4.0
slot_length = 20.0
slot_offset_x = -20.0
slot_offset_y = 10.0

base = Box(plate_width, plate_height, plate_thickness)
rib = Pos(0, plate_height/2 + rib_thickness/2, 0) * Box(rib_width, rib_thickness, rib_height)
result = base + rib

result = result - Pos(hole_offset_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, 20)
result = result - Pos(slot_offset_x, slot_offset_y, 0) * Box(slot_length, slot_width, 20)

part = result
part.name = "plate_with_rib_hole_slot"
export_step(part, "output.step")