from build123d import *

block_length = 70.0
block_width = 30.0
block_height = 20.0
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 6.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.8
fillet_radius = 0.5
tab_length = 10.0
tab_width = 8.0
tab_height = 5.0
slot_width = 3.0
slot_height = 8.0
slot_depth = 5.0

solid_body = Box(block_length, block_width, block_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, 0, -block_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [(0, 0), (-hole_spacing/2, -hole_spacing/2), (hole_spacing/2, -hole_spacing/2)]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, block_height)

tab = Pos(block_length/2 + tab_height/2, 0, 0) * Box(tab_height, tab_width, tab_length)
solid_body = solid_body + tab

slot = Pos(block_length/2 + tab_height - slot_depth/2, 0, tab_length/2 - slot_height/2) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot

part = solid_body
part.name = "block_with_pocket_holes_tab_slot"
export_step(part, "output.step")