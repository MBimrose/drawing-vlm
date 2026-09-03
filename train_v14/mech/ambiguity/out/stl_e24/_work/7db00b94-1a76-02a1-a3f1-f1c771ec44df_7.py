from build123d import *

block_width = 80.0
block_depth = 80.0
block_thickness = 20.0
slot_width = 12.0
slot_depth = 15.0
hole_diameter = 4.5
hole_rows = 2
hole_cols = 4
hole_spacing_x = 20.0
hole_spacing_y = 30.0
hole_offset_x = 10.0
hole_offset_y = 10.0
fillet_radius = 2.0
boss_radius = 8.0
boss_height = 5.0

solid_body = Box(block_width, block_depth, block_thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

slot_cut = Pos(0, block_depth/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, block_thickness)
solid_body = solid_body - slot_cut

boss = Pos(0, 0, -block_thickness/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = -block_width/2 + hole_offset_x + i * hole_spacing_x
        y = -block_depth/2 + hole_offset_y + j * hole_spacing_y
        hole = Pos(x, y, block_thickness/2) * Cylinder(hole_diameter/2, block_thickness + 1)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_slot_boss_and_holes"
export_step(part, "output.step")