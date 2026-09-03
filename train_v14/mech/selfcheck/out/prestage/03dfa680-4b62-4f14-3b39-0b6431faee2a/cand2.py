from build123d import *

plate_length = 80.0
plate_width = 80.0
plate_thickness = 8.0
pocket_length = 50.0
pocket_width = 50.0
pocket_depth = 6.0
rib_width = 12.0
rib_height = 6.0
rib_offset = 5.0
hole_diameter = 3.0
chamfer_size = 1.0
slot_length = 30.0
slot_width = 5.0
slot_offset_y = -plate_width/2 + 10.0

base = Box(plate_length, plate_width, plate_thickness)

rib_positions = [
    (plate_length/2 - rib_offset - rib_width/2, plate_width/2 - rib_offset - rib_width/2),
    (-plate_length/2 + rib_offset + rib_width/2, plate_width/2 - rib_offset - rib_width/2),
    (-plate_length/2 + rib_offset + rib_width/2, -plate_width/2 + rib_offset + rib_width/2),
    (plate_length/2 - rib_offset - rib_width/2, -plate_width/2 + rib_offset + rib_width/2),
]

result = base
for x, y in rib_positions:
    result = result + Pos(x, y, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_width, rib_height)

result = result - Pos(0, 0, plate_thickness/2 + rib_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

for x, y in rib_positions:
    result = result - Pos(x, y, plate_thickness/2 + rib_height/2) * Cylinder(hole_diameter/2, rib_height + plate_thickness + 1)

result = result - Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness + 1)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_ribs_pocket_holes_slot"
export_step(part, "output.step")