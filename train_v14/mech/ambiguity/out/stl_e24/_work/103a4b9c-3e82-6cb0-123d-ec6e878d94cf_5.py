from build123d import *

block_length = 70
block_width = 30
block_height = 20
wall_thickness = 2
tab_width = 10
tab_height = 12
tab_thickness = 5
pocket_length = 40
pocket_width = 15
pocket_depth = 6
fillet_radius = 0.5
chamfer_distance = 0.8
mount_hole_dia = 3
mount_hole_spacing = 30
cable_hole_dia = 4
cable_hole_offset = 5

solid_body = Box(block_length, block_width, block_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

tab = Pos(block_length/2 + tab_thickness/2, 0, 0) * Box(tab_thickness, tab_width, tab_height)
solid_body = solid_body + tab

pocket_cut = Pos(block_length/2 + tab_thickness - pocket_depth/2, 0, tab_height/4) * Box(pocket_depth, pocket_width/2, tab_height/2)
solid_body = solid_body - pocket_cut

bottom_pocket = Pos(0, 0, -block_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - bottom_pocket

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(0, y, 0) * Cylinder(mount_hole_dia/2, block_height * 2)

solid_body = solid_body - Pos(0, 0, 0) * Cylinder(cable_hole_dia/2, block_height * 2)

part = solid_body
part.name = "block_with_tab_and_pockets"
export_step(part, "output.step")