from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 30.0
rib_width = 20.0
rib_length = 40.0
rib_height = 10.0
hole_diameter = 12.0
hole_offset_x = 20.0
hole_offset_y = 15.0
corner_hole_diameter = 6.0
corner_hole_offset = 15.0
pocket_width = 30.0
pocket_height = 10.0
pocket_depth = 20.0
chamfer_size = 2.0
fillet_radius = 4.0

solid = Box(block_length, block_width, block_height)
solid = solid + Pos(0, 0, rib_height/2) * Box(rib_width, rib_length, rib_height)

hole_x = hole_offset_x - block_length/2
hole_y = hole_offset_y - block_width/2
solid = solid - Pos(hole_x, hole_y, 0) * Cylinder(hole_diameter/2, block_height + rib_height + 10)

corner_x = corner_hole_offset - block_length/2
corner_y = corner_hole_offset - block_width/2
for cx, cy in [(corner_x, corner_y), (-corner_x, corner_y), (corner_x, -corner_y), (-corner_x, -corner_y)]:
    solid = solid - Pos(cx, cy, 0) * Cylinder(corner_hole_diameter/2, block_height + rib_height + 10)

solid = solid - Pos(0, -block_width/2 + pocket_depth/2, 0) * Box(pocket_width, pocket_depth, pocket_height)

top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = chamfer(top_face.edges(), chamfer_size)

right_face = solid.faces().sort_by(Axis.X)[-1]
solid = fillet(right_face.edges().filter_by(Axis.Z), fillet_radius)

part = solid
part.name = "block_with_rib_holes_pocket"
export_step(part, "output.step")