from build123d import *

block_length = 80.0
block_width = 30.0
block_height = 10.0
pocket_length = 40.0
pocket_width = 20.0
pocket_depth = 4.0
pocket_offset = 5.0
hole_diameter = 4.0
cbore_diameter = 7.0
cbore_depth = 2.0
hole_offset_x = 12.0
hole_offset_y = 0.0
chamfer_size = 1.0
rib_height = 2.0
rib_thickness = 3.0
rib_spacing = 10.0

solid_body = Box(block_length, block_width, block_height)

pocket_x = -block_length/2 + pocket_offset + pocket_length/2
pocket_z = block_height - pocket_depth/2
solid_body = solid_body - Pos(pocket_x, 0, pocket_z) * Box(pocket_length, pocket_width, pocket_depth)

hole_x = block_length/2 - hole_offset_x
solid_body = solid_body - Pos(hole_x, hole_offset_y, 0) * Cylinder(hole_diameter/2, block_height)
solid_body = solid_body - Pos(hole_x, hole_offset_y, -block_height/2 + cbore_depth/2) * Cylinder(cbore_diameter/2, cbore_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib1_x = -block_length/2 + rib_spacing + rib_thickness/2
rib_z = rib_height/2
solid_body = solid_body + Pos(rib1_x, 0, rib_z) * Box(rib_thickness, block_width - 2*rib_spacing, rib_height)

rib2_x = block_length/2 - rib_spacing - rib_thickness/2
solid_body = solid_body + Pos(rib2_x, 0, rib_z) * Box(rib_thickness, block_width - 2*rib_spacing, rib_height)

part = solid_body
part.name = "block_with_pocket_hole_chamfer_ribs"
export_step(part, "output.step")