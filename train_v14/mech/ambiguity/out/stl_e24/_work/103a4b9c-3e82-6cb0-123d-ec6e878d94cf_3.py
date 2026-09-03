from build123d import *

block_length = 70.0
block_width = 30.0
block_height = 20.0
wall_thickness = 2.0
tab_width = 10.0
tab_height = 8.0
tab_thickness = 5.0
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 6.0
fillet_radius = 0.5
chamfer_distance = 1.0
mount_hole_dia = 3.0
mount_hole_spacing = 30.0
central_hole_dia = 4.0
slot_width = 5.0
slot_height = 12.0
slot_depth = 3.0

result = Box(block_length, block_width, block_height)
result = result + Pos(block_length/2 + tab_thickness/2, 0, 0) * Box(tab_thickness, tab_width, tab_height)
result = result - Pos(0, 0, -block_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - Cylinder(central_hole_dia/2, block_height)
result = result - Pos(0, -mount_hole_spacing/2, 0) * Cylinder(mount_hole_dia/2, block_height)
result = result - Pos(0, mount_hole_spacing, 0) * Cylinder(mount_hole_dia/2, block_height)
result = result - Pos(block_length/2 + tab_thickness - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_height)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "block_with_tab_pocket_and_holes"
export_step(part, "output.step")