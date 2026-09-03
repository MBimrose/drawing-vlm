from build123d import *

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 8.0
pocket_width = 50.0
pocket_depth = 50.0
pocket_cut_depth = 6.0
boss_width = 12.0
boss_depth = 12.0
boss_height = 6.0
boss_offset = 10.0
hole_diameter = 3.0
slot_width = 30.0
slot_depth = 4.0
chamfer_size = 0.5

base = Box(plate_width, plate_depth, plate_thickness)

pocket = Pos(0, 0, plate_thickness - pocket_cut_depth/2) * Box(pocket_width, pocket_depth, pocket_cut_depth)
base = base - pocket

slot = Pos(0, -plate_depth/2 + slot_depth/2, plate_thickness/2) * Box(slot_width, slot_depth, plate_thickness)
base = base - slot

boss_positions = [
    (plate_width/2 - boss_offset - boss_width/2, plate_depth/2 - boss_offset - boss_depth/2),
    (-plate_width/2 + boss_offset + boss_width/2, plate_depth/2 - boss_offset - boss_depth/2),
    (-plate_width/2 + boss_offset + boss_width/2, -plate_depth/2 + boss_offset + boss_depth/2),
    (plate_width/2 - boss_offset - boss_width/2, -plate_depth/2 + boss_offset + boss_depth/2),
]

result = base
for x, y in boss_positions:
    boss = Pos(x, y, plate_thickness/2 + boss_height/2) * Box(boss_width, boss_depth, boss_height)
    result = result + boss

for x, y in boss_positions:
    hole = Pos(x, y, plate_thickness/2 + boss_height/2) * Cylinder(hole_diameter/2, boss_height + 0.1)
    result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_pocket_slot_bosses"
export_step(part, "output.step")