from build123d import *

block_width = 80.0
block_length = 80.0
block_height = 20.0
slot_width = 12.0
slot_depth = 15.0
hole_diameter = 4.5
hole_spacing_x = 20.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 4
edge_fillet_radius = 2.0
boss_radius = 8.0
boss_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_width, block_length)
    extrude(amount=block_height)

solid_body = p.part
solid_body = fillet(solid_body.edges(), edge_fillet_radius)

slot = Pos(0, block_length/2 - slot_depth/2, block_height/2) * Box(slot_width, slot_depth, block_height)
solid_body = solid_body - slot

boss = Pos(0, 0, -boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

for row in range(hole_rows):
    for col in range(hole_cols):
        x = (col - (hole_cols - 1) / 2) * hole_spacing_x
        y = (row - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, block_height/2) * Cylinder(hole_diameter/2, block_height + 1)
        solid_body = solid_body - hole

part = solid_body
part.name = "block_with_slot_boss_and_holes"
export_step(part, "output.step")