from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 6.0
lip_height = 2.0
lip_width = 5.0
slot_length = 50.0
slot_width = 5.0
hole_diameter = 6.0
hole_offset = 12.0
chamfer_dist = 0.8
fillet_radius = 0.5
boss_diameter = 15.0
boss_height = 8.0

base = Box(plate_length, plate_width, plate_thickness)
lip = Pos(0, 0, plate_thickness/2 + lip_height/2) * Box(plate_length + 2*lip_width, plate_width + 2*lip_width, lip_height)
result = base + lip

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + lip_height + 20, both=True)
result = result - slot_bp.part

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + lip_height + 20)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_dist)
bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), fillet_radius)

boss = Pos(0, 0, plate_thickness/2 + lip_height + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

part = result
part.name = "plate_with_lip_slot_holes_boss"
export_step(part, "output.step")