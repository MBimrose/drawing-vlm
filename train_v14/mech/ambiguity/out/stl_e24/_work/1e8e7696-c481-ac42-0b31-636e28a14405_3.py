from build123d import *

plate_length = 100
plate_width = 80
plate_thickness = 6
flange_length = 20
flange_width = plate_width
flange_thickness = plate_thickness
slot_length = 40
slot_width = 20
slot_offset_from_edge = 10
boss_size = 30
boss_height = 4
hole_diameter = 6
hole_spacing = 12
chamfer_size = 1

base = Box(plate_length, plate_width, plate_thickness)
flange = Pos(plate_length/2 + flange_length/2, 0, 0) * Box(flange_length, flange_width, flange_thickness)
result = base + flange

slot_center_x = -plate_length/2 + slot_offset_from_edge + slot_length/2
slot = Pos(slot_center_x, 0, 0) * Box(slot_length, slot_width, plate_thickness + 2)
result = result - slot

boss_center_x = plate_length/2 - boss_size/2 - 5
boss = Pos(boss_center_x, 0, plate_thickness/2 + boss_height/2) * Box(boss_size, boss_size, boss_height)
result = result + boss

hole_positions = [
    (boss_center_x - hole_spacing/2, -hole_spacing/2),
    (boss_center_x + hole_spacing/2, -hole_spacing/2),
    (boss_center_x - hole_spacing/2, hole_spacing/2),
    (boss_center_x + hole_spacing/2, hole_spacing/2),
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2 + boss_height/2) * Cylinder(hole_diameter/2, boss_height)
    result = result - hole

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_flange_slot_boss"
export_step(part, "output.step")