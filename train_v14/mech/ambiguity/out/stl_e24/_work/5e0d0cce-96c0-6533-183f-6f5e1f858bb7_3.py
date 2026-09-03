from build123d import *

block_length = 80.0
block_width = 40.0
block_height = 20.0
slot_width = 10.0
slot_length = 30.0
slot_offset = 25.0
chamfer_size = 1.0
fillet_radius = 1.5
hole_diameter = 5.0
hole_edge_margin = 5.0
boss_diameter = 12.0
boss_height = 4.0

solid_body = Box(block_width, block_length, block_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

slot_center_y = (block_length / 2) - slot_offset - (slot_length / 2)
slot_cut = Pos(0, slot_center_y, 0) * Box(slot_width, slot_length, block_height)
solid_body = solid_body - slot_cut

boss = Pos(0, 0, block_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

px = block_width / 2 - hole_edge_margin - hole_diameter / 2
py = block_length / 2 - hole_edge_margin - hole_diameter / 2
for x, y in [(px, py), (-px, py), (-px, -py), (px, -py)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, block_height + boss_height + 10)

part = solid_body
part.name = "chamfered_block_with_slot_boss_holes"
export_step(part, "output.step")