from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 15.0
slot_length = 30.0
slot_width = 10.0
groove_width = 5.0
groove_depth = 4.0
hole_diameter = 5.0
hole_offset_x = 20.0
hole_offset_y = 15.0

result = Box(plate_length, plate_width, plate_thickness)

slot = Box(slot_length, slot_width, plate_thickness)
result = result - slot

groove = Pos(0, 0, plate_thickness/2 - groove_depth/2) * Box(plate_length - 2*groove_width, plate_width - 2*groove_width, groove_depth)
result = result - groove

hole_positions = [
    (-plate_length/2 + hole_offset_x, -plate_width/2 + hole_offset_y),
    ( plate_length/2 - hole_offset_x, -plate_width/2 + hole_offset_y),
    (-plate_length/2 + hole_offset_x,  plate_width/2 - hole_offset_y),
    ( plate_length/2 - hole_offset_x,  plate_width/2 - hole_offset_y),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

part = result
part.name = "plate_with_slot_groove_holes"
export_step(part, "output.step")