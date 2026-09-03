from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
slot_width = 8.0
slot_depth = 12.0
slot_spacing = 15.0
num_slots = 4
fillet_radius = 0.8
chamfer_distance = 1.2
hole_diameter = 4.0
hole_depth = 8.0
hole_offset = 10.0

solid_body = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)

for i in range(num_slots):
    x = (i - (num_slots - 1) / 2) * slot_spacing
    slot = Pos(x, 0, block_height - slot_depth/2) * Box(slot_width, block_width, slot_depth)
    solid_body = solid_body - slot

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (hole_offset, -hole_offset), (-hole_offset, -hole_offset)]:
    hole = Pos(x, y, hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "slotted_block_with_holes"
export_step(part, "output.step")