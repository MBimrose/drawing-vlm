from build123d import *

plate_length = 80.0
plate_width = 80.0
plate_thickness = 8.0
pocket_length = 50.0
pocket_width = 50.0
pocket_depth = 6.0
pocket_chamfer = 2.0
hole_diameter = 3.0
hole_offset = 12.0
rib_width = 12.0
rib_height = 6.0
slot_length = 30.0
slot_width = 6.0
slot_offset = 5.0

base = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
pocket = chamfer(pocket.edges(), pocket_chamfer)
base = base - pocket

rib = Box(rib_width, rib_width, rib_height)
rib_positions = [
    (plate_length/2 - rib_width/2 - hole_offset, plate_width/2 - rib_width/2 - hole_offset),
    (-plate_length/2 + rib_width/2 + hole_offset, plate_width/2 - rib_width/2 - hole_offset),
    (-plate_length/2 + rib_width/2 + hole_offset, -plate_width/2 + rib_width/2 + hole_offset),
    (plate_length/2 - rib_width/2 - hole_offset, -plate_width/2 + rib_width/2 + hole_offset)
]
for x, y in rib_positions:
    base = base + Pos(x, y, plate_thickness/2 + rib_height/2) * rib

hole = Cylinder(hole_diameter/2, plate_thickness + rib_height + 2)
for x, y in rib_positions:
    base = base - Pos(x, y, plate_thickness/2 + rib_height/2) * hole

slot = Pos(0, -plate_width/2 + slot_offset, 0) * Box(slot_length, slot_width, plate_thickness + 2)
base = base - slot

part = base
part.name = "plate_with_pocket_ribs_and_slot"
export_step(part, "output.step")