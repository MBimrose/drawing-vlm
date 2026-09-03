from build123d import *

block_length = 80.0
block_width = 80.0
block_thickness = 20.0
slot_width = 10.0
slot_length = 30.0
hole_diameter = 4.5
hole_spacing_x = 20.0
hole_spacing_y = 60.0
hole_rows = 2
hole_columns = 4
fillet_radius = 2.0
boss_radius = 8.0
boss_height = 5.0

solid_body = Box(block_length, block_width, block_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

slot = Pos(0, block_width/2, 0) * Box(slot_width, slot_length, block_thickness)
solid_body = solid_body - slot

for i in range(hole_columns):
    for j in range(hole_rows):
        x = (i - (hole_columns - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        solid_body = solid_body - Pos(x, y, block_thickness/2) * Cylinder(hole_diameter/2, block_thickness + 1)

boss = Pos(0, 0, -block_thickness/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "block_with_slot_holes_and_boss"
export_step(part, "output.step")