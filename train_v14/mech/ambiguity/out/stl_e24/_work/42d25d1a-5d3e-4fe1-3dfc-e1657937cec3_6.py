from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
wall_thickness = 4.0
slot_width = 6.0
slot_depth = 12.0
slot_spacing = 18.0
num_slots = 3
fillet_radius = 0.8
chamfer_distance = 1.2
hole_diameter = 4.0
hole_offset = 10.0

solid = Box(block_length, block_width, block_height)

for i in range(num_slots):
    x = (i - (num_slots - 1) / 2) * slot_spacing
    solid = solid - Pos(x, 0, block_height/2 - slot_depth/2) * Box(slot_width, block_width, slot_depth)

bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = chamfer(bottom_face.edges(), chamfer_distance)

solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (-hole_offset, -hole_offset), (hole_offset, -hole_offset)]:
    solid = solid - Pos(x, y, -block_height/2 + wall_thickness) * Cylinder(hole_diameter/2, wall_thickness * 2)

part = solid
part.name = "slot_block_with_holes"
export_step(part, "output.step")