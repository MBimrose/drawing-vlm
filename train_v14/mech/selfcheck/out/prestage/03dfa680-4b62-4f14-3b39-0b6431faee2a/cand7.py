from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 8.0
rib_height = 6.0
rib_width = 12.0
rib_offset = 10.0
hole_diameter = 3.0
pocket_width = 50.0
pocket_depth = 50.0
pocket_depth_cut = 4.0
slot_length = 30.0
slot_width = 5.0
slot_offset = 5.0
chamfer_size = 0.5

result = Box(plate_width, plate_depth, plate_thickness)

rib_positions = [
    (-plate_width/2 + rib_offset, -plate_depth/2 + rib_offset),
    ( plate_width/2 - rib_offset, -plate_depth/2 + rib_offset),
    (-plate_width/2 + rib_offset,  plate_depth/2 - rib_offset),
    ( plate_width/2 - rib_offset,  plate_depth/2 - rib_offset)
]

for x, y in rib_positions:
    result = result + Pos(x, y, plate_thickness) * Box(rib_width, rib_width, rib_height)

for x, y in rib_positions:
    result = result - Pos(x, y, plate_thickness + rib_height/2) * Cylinder(hole_diameter/2, rib_height + 0.2)

result = result - Pos(0, 0, plate_thickness - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)

result = result - Pos(0, -plate_depth/2 + slot_offset, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness + 0.2)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_ribs_pocket_slot"
export_step(part, "output.step")