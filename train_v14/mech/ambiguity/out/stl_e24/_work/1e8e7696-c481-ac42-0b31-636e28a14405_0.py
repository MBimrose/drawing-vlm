from build123d import *

plate_length = 120.0
plate_width = 80.0
plate_thickness = 6.0
slot_length = 40.0
slot_width = 20.0
slot_offset = 10.0
boss_size = 30.0
boss_height = 4.0
hole_diameter = 6.0
hole_spacing = 12.0
hole_rows = 2
hole_cols = 2
chamfer_size = 1.0

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

slot_center_x = -plate_length/2 + slot_offset + slot_length/2
slot = Pos(slot_center_x, 0, 0) * Box(slot_length, slot_width, plate_thickness)
base = base - slot

boss_center_x = plate_length/2 - boss_size/2 - 10.0
boss = Pos(boss_center_x, 0, plate_thickness/2 + boss_height/2) * Box(boss_size, boss_size, boss_height)
base = base + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = boss_center_x + (i - (hole_cols-1)/2) * hole_spacing
        y = (j - (hole_rows-1)/2) * hole_spacing
        hole = Pos(x, y, plate_thickness/2 + boss_height/2) * Cylinder(hole_diameter/2, boss_height)
        base = base - hole

part = base
part.name = "plate_with_slot_boss_and_holes"
export_step(part, "output.step")