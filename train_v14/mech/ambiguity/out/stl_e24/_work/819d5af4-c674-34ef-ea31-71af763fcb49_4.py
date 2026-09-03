from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_height = 2.0
rib_width = 5.0
slot_length = 50.0
slot_width = 5.0
hole_diameter = 6.0
hole_offset = 12.0
chamfer_size = 1.0
boss_diameter = 15.0
boss_height = 8.0

base = Box(plate_length, plate_width, plate_thickness)
rib = Pos(0, 0, plate_thickness) * Box(plate_length + 2*rib_width, plate_width + 2*rib_width, rib_height)
result = base + rib

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + rib_height + 20, both=True)
result = result - slot_bp.part

hole_positions = [
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 20)

boss = Pos(0, 0, plate_thickness + rib_height) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_rib_slot_holes_boss"
export_step(part, "output.step")