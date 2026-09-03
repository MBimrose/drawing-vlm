from build123d import *

plate_width = 60.0
plate_height = 40.0
plate_thickness = 5.0
rib_width = 8.0
rib_height = 3.0
rib_length = plate_width - 10.0
rib_offset_y = plate_height/2 - rib_height/2
slot_width = 4.0
slot_length = 20.0
slot_offset_x = -plate_width/4
slot_offset_y = plate_height/4
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_y = plate_height/2 - 5.0
chamfer_size = 0.2

base = Box(plate_width, plate_height, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, rib_offset_y, 0) * Box(rib_length, rib_height, rib_width)
result = base + rib

slot = Pos(slot_offset_x, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness + 10)
result = result - slot

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

part = result
part.name = "plate_with_rib_slot_holes"
export_step(part, "output.step")