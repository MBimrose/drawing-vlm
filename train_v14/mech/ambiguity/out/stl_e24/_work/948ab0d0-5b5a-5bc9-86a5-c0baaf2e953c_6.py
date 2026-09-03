from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_length = 40.0
slot_width = 20.0
rib_height = 12.0
rib_thickness = 6.0
hole_diameter = 4.0
hole_offset = 20.0
chamfer_distance = 1.0

result = Box(plate_length, plate_width, plate_thickness)

slot = Box(slot_width, slot_length, plate_thickness)
result = result - slot

rib_top = Pos(0, plate_width/2 - rib_thickness/2, 0) * Box(plate_length, rib_thickness, rib_height)
result = result + rib_top

rib_bottom = Pos(0, -plate_width/2 + rib_thickness/2, 0) * Box(plate_length, rib_thickness, rib_height)
result = result + rib_bottom

for x in [-hole_offset, hole_offset]:
    result = result - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

part = result
part.name = "plate_with_slot_ribs_and_holes"
export_step(part, "output.step")