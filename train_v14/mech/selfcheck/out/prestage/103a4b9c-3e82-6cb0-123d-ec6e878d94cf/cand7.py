from build123d import *

block_length = 70.0
block_width = 30.0
block_height = 20.0
wall_thickness = 2.0
tab_width = 10.0
tab_height = 12.0
tab_thickness = 5.0
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 5.0
fillet_radius = 0.5
chamfer_distance = 0.8
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
rib_thickness = 2.0
rib_height = 5.0

result = Box(block_length, block_width, block_height)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)

tab = Pos(block_length/2 + tab_thickness/2, 0, 0) * Box(tab_thickness, tab_width, tab_height)
result = result + tab

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

pocket = Pos(0, 0, -block_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

for x, y in [(0, -mount_hole_spacing/2), (0, mount_hole_spacing/2)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, block_height + 10)

rib = Pos(block_length/2 + tab_thickness/2, 0, tab_height/2 - rib_height/2) * Box(rib_thickness, rib_thickness, rib_height)
result = result - rib

part = result
part.name = "block_with_tab_pocket_and_holes"
export_step(part, "output.step")