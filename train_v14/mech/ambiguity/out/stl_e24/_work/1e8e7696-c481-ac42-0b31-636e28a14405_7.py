from build123d import *

plate_length = 120.0
plate_width = 80.0
plate_thickness = 6.0
chamfer_size = 1.0
slot_length = 40.0
slot_width = 20.0
slot_offset_x = -plate_length / 4.0
slot_offset_y = 0.0
boss_size = 30.0
boss_height = 4.0
boss_offset_x = plate_length / 4.0
boss_offset_y = 0.0
hole_diameter = 6.0
hole_spacing = 12.0
hole_rows = 2
hole_cols = 2

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

slot = Pos(slot_offset_x, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness * 2)
solid_body = solid_body - slot

boss = Pos(boss_offset_x, boss_offset_y, plate_thickness / 2 + boss_height / 2) * Box(boss_size, boss_size, boss_height)
solid_body = solid_body + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = boss_offset_x + (i - (hole_cols - 1) / 2) * hole_spacing
        y = boss_offset_y + (j - (hole_rows - 1) / 2) * hole_spacing
        hole = Pos(x, y, plate_thickness / 2 + boss_height / 2) * Cylinder(hole_diameter / 2, boss_height)
        solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_slot_boss_and_holes"
export_step(part, "output.step")