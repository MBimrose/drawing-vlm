from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 10.0
boss_diameter = 15.0
boss_height = 8.0
hole_diameter = 6.0
hole_offset = 12.0
slot_width = 20.0
slot_depth = 5.0
chamfer_size = 0.5
pocket_depth = 2.0

base = Box(plate_length, plate_width, plate_thickness)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length, plate_width, rib_height)
rib = rib - Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(plate_length - 2*rib_width, plate_width - 2*rib_width, rib_height)

boss = Pos(0, 0, plate_thickness/2 + rib_height + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

result = base + rib + boss

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_width, slot_depth)
    extrude(amount=plate_thickness + 10)
result = result - slot_bp.part

result = chamfer(result.edges(), chamfer_size)

pocket = Pos(0, 0, -plate_thickness/2 - pocket_depth/2) * Box(plate_length - 2*hole_offset, plate_width - 2*hole_offset, pocket_depth)
result = result - pocket

part = result
part.name = "plate_with_rib_boss_holes"
export_step(part, "output.step")