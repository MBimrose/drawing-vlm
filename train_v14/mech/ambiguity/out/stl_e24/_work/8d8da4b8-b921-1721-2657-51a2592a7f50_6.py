from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
pocket_chamfer = 0.5
mount_hole_dia = 5.0
mount_hole_offset = 8.0
slot_length = 25.0
slot_width = 6.0
slot_offset = plate_width/2 - slot_width/2 - 5.0
rib_width = 8.0
rib_height = 2.0

result = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
pocket_edges = pocket.edges().filter_by(Axis.Z)
pocket = chamfer(pocket_edges, pocket_chamfer)
result = result - pocket

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

result = result - Pos(0, slot_offset, 0) * Box(slot_length, slot_width, plate_thickness)
result = result - Pos(0, -slot_offset, 0) * Box(slot_length, slot_width, plate_thickness)

rib = Pos(0, 0, rib_height/2) * Box(rib_width, rib_width, rib_height)
result = result + rib

part = result
part.name = "plate_with_pocket_holes_slots_rib"
export_step(part, "output.step")