from build123d import *

block_length = 100.0
block_width = 50.0
block_thickness = 10.0
pocket_length = 80.0
pocket_width = 30.0
pocket_depth = 5.0
chamfer_size = 0.5
hole_diameter = 3.0
hole_offset_x = 35.0
hole_offset_y = 15.0
rib_height = 5.0
rib_width = 5.0
rib_spacing = 20.0

solid_body = Box(block_length, block_width, block_thickness)

pocket = Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

hole_positions = [
    (hole_offset_x, hole_offset_y),
    (-hole_offset_x, hole_offset_y),
    (hole_offset_x, -hole_offset_y),
    (-hole_offset_x, -hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_thickness)

num_ribs = int(block_length / rib_spacing) + 1
for i in range(num_ribs):
    x_pos = -block_length/2 + i * rib_spacing
    rib = Pos(x_pos, 0, -block_thickness/2 - rib_height/2) * Box(rib_width, rib_height, rib_height)
    solid_body = solid_body + rib

part = solid_body
part.name = "block_with_pocket_ribs"
export_step(part, "output.step")