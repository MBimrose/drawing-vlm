from build123d import *

arm_length = 80.0
arm_width = 30.0
arm_thickness = 10.0
groove_width = 6.0
groove_depth = 4.0
groove_length = 60.0
bearing_diameter = 20.0
bearing_depth = 8.0
chamfer_distance = 1.0
mount_hole_diameter = 4.0
mount_hole_spacing = 15.0
rib_height = 3.0
rib_thickness = 2.0
rib_spacing = 20.0

result = Pos(0, 0, arm_thickness/2) * Box(arm_length, arm_width, arm_thickness)

groove = Pos(0, 0, arm_thickness - groove_depth/2) * Box(groove_width, groove_length, groove_depth)
result = result - groove

bearing = Pos(arm_length/2 - bearing_depth/2, 0, bearing_depth/2) * Cylinder(bearing_diameter/2, bearing_depth)
result = result - bearing

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(-arm_length/4, y, arm_thickness/2) * Cylinder(mount_hole_diameter/2, arm_thickness + 2)
    result = result - hole

rib = Pos(-arm_length/4, 0, rib_height/2) * Box(rib_thickness, arm_width, rib_height)
result = result + rib

z_edges = result.edges().filter_by(Axis.Z)
min_x = min(e.center().X for e in z_edges)
chamfer_edges = [e for e in z_edges if abs(e.center().X - min_x) < 0.1]
result = chamfer(chamfer_edges, chamfer_distance)

part = result
part.name = "arm_with_groove_and_bearing"
export_step(part, "output.step")