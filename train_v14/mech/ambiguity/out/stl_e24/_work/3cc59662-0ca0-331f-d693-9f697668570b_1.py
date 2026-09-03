from build123d import *

block_length = 60.0
block_width = 40.0
block_height = 20.0
central_hole_diameter = 20.0
counterbore_diameter = 24.0
counterbore_depth = 5.0
corner_hole_diameter = 6.0
corner_hole_offset = 15.0
fillet_radius = 2.0
slot_width = 15.0
slot_length = 20.0
slot_depth = 5.0
boss_height = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, block_height/2) * Cylinder(central_hole_diameter/2, block_height)
solid_body = solid_body - Pos(0, 0, block_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

for x, y in [(corner_hole_offset, corner_hole_offset), (-corner_hole_offset, corner_hole_offset),
             (-corner_hole_offset, -corner_hole_offset), (corner_hole_offset, -corner_hole_offset)]:
    solid_body = solid_body - Pos(x, y, block_height/2) * Cylinder(corner_hole_diameter/2, block_height)

solid_body = solid_body + Pos(0, 0, block_height + boss_height/2) * Cylinder(counterbore_diameter/2, boss_height)
solid_body = solid_body - Pos(0, block_width/2 - slot_depth/2, block_height/2) * Box(slot_width, slot_depth, slot_length)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "block_with_holes_and_slot"
export_step(part, "output.step")