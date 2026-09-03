from build123d import *

body_length = 70.0
body_width = 30.0
body_height = 20.0
wall_thickness = 2.0
pocket_length = 40.0
pocket_width = 15.0
pocket_depth = 5.0
latch_width = 10.0
latch_height = 12.0
latch_thickness = 5.0
latch_flex_width = 3.0
latch_flex_height = 8.0
latch_flex_depth = 2.5
fillet_radius = 0.5
chamfer_distance = 0.8
mount_hole_dia = 3.0
mount_hole_spacing = 30.0
central_hole_dia = 4.0

result = Box(body_length, body_width, body_height)
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_distance)
result = result - Pos(0, 0, -body_height/2 + pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - Cylinder(central_hole_dia/2, body_height)
for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(0, y, 0) * Cylinder(mount_hole_dia/2, body_height)
latch = Pos(body_length/2 + latch_thickness/2, 0, 0) * Box(latch_thickness, latch_width, latch_height)
result = result + latch
result = result - Pos(body_length/2 + latch_thickness - latch_flex_depth/2, 0, latch_height/2 - latch_flex_height/2) * Box(latch_flex_depth, latch_flex_width, latch_flex_height)
result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "box_with_latch"
export_step(part, "output.step")