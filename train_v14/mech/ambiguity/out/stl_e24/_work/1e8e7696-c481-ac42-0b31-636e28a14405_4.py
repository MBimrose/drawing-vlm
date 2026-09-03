from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
flange_width = 20.0
boss_size = 30.0
boss_height = 4.0
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 12.0
chamfer_size = 1.0
slot_length = 40.0
slot_width = 20.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length + 2*flange_width, plate_width + 2*flange_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

slot = Pos(-plate_length/2 + slot_length/2, 0, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
base = base - slot

boss = Pos(plate_length/2 - boss_size/2, 0, plate_thickness + boss_height/2) * Box(boss_size, boss_size, boss_height)
base = base + boss

hole_positions = [
    (plate_length/2 - boss_size/2 - hole_spacing/2, -hole_spacing/2),
    (plate_length/2 - boss_size/2 + hole_spacing/2, -hole_spacing/2),
    (plate_length/2 - boss_size/2 - hole_spacing/2, hole_spacing/2),
    (plate_length/2 - boss_size/2 + hole_spacing/2, hole_spacing/2),
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness + boss_height - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    base = base - hole

part = base
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")