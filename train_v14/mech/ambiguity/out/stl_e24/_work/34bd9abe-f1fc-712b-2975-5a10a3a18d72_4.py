from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
pocket_width = 20.0
pocket_depth = 10.0
slot_width = 5.0
slot_length = block_width
fillet_radius = 1.0
hole_diameter = 5.0
hole_spacing = 30.0

result = Box(block_length, block_width, block_height)

pocket = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(pocket_width, pocket_width, pocket_depth)
result = result - pocket

slot = Pos(0, 0, block_height/2 - pocket_depth/2) * Box(slot_width, slot_length, pocket_depth)
result = result - slot

for y in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, block_length)
    result = result - hole

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = fillet(bottom_edges, fillet_radius)

part = result
part.name = "block_with_pocket_slot_holes"
export_step(part, "output.step")