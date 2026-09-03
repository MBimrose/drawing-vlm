from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
pocket_width = 10.0
pocket_depth = 5.0
pocket_spacing = 20.0
pocket_offset_y = 15.0
hole_diameter = 4.0
hole_spacing = 20.0
chamfer_size = 1.2
fillet_radius = 0.8

solid_body = Box(block_length, block_width, block_height)

pocket_z = block_height - pocket_depth / 2
for x in [-pocket_spacing, 0, pocket_spacing]:
    solid_body = solid_body - Pos(x, pocket_offset_y, pocket_z) * Box(pocket_width, pocket_width, pocket_depth)

hole_r = hole_diameter / 2
for x in [-hole_spacing/2, hole_spacing/2]:
    for y in [-hole_spacing/2, hole_spacing/2]:
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, block_height)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "block_with_pockets_holes_chamfer_fillet"
export_step(part, "output.step")