from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
groove_width = 12.0
groove_depth = 8.0
fillet_radius = 1.0
hole_diameter = 5.0
hole_spacing = 30.0
rib_width = 6.0
rib_height = 4.0
rib_spacing = 15.0

result = Box(block_length, block_width, block_height)

groove = Pos(0, 0, block_height/2 - groove_depth/2) * Box(groove_width, block_length, groove_depth)
result = result - groove

for y in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(0, y, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, block_length)
    result = result - hole

rib_count = int((block_width - rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    y_pos = -block_width/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(0, y_pos, -block_height/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
    result = result + rib

vertical_edges = result.edges().filter_by(Axis.Z)
result = fillet(vertical_edges, fillet_radius)

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = fillet(bottom_edges, fillet_radius)

part = result
part.name = "grooved_block_with_ribs"
export_step(part, "output.step")