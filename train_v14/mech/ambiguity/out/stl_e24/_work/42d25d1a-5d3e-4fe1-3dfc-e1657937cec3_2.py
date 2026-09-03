from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
slot_width = 8.0
slot_depth = 12.0
slot_spacing = 20.0
slot_count = 3
chamfer_size = 1.2
fillet_radius = 0.8
hole_diameter = 4.0
hole_offset = 10.0

solid_body = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

for i in range(slot_count):
    x_pos = -block_length/2 + slot_spacing + i * slot_spacing
    slot = Pos(x_pos, 0, block_height - slot_depth/2) * Box(slot_width, block_width, slot_depth)
    solid_body = solid_body - slot

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (hole_offset, -hole_offset), (-hole_offset, -hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height + 1)

part = solid_body
part.name = "slotted_block_with_holes"
export_step(part, "output.step")