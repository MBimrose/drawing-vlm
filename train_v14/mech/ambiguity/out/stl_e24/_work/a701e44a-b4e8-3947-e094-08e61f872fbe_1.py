from build123d import *

body_width = 40.0
body_height = 40.0
thickness = 8.0
arm_length = 30.0
arm_width = 20.0
fillet_radius = 4.0
hole_diameter = 6.0
rib_width = 6.0
rib_height = 12.0
rib_spacing = 12.0
rib_thickness = 2.0

base = Box(body_width, body_height, thickness)
arm = Pos(body_width/2 - arm_width/2, body_height/2 + arm_length/2, 0) * Box(arm_width, arm_length, thickness)
result = base + arm

z_edges = result.edges().filter_by(Axis.Z)
max_x = max(e.center().X for e in z_edges)
fillet_edges = [e for e in z_edges if abs(e.center().X - max_x) < 0.01]
result = fillet(fillet_edges, fillet_radius)

hole_center_x = body_width/2 - arm_width/2
hole_center_y = body_height/2 + arm_length/2
result = result - Pos(hole_center_x, hole_center_y, 0) * Cylinder(hole_diameter/2, thickness * 2)

num_ribs = int((body_width - rib_spacing) // rib_spacing)
for i in range(num_ribs):
    x_pos = -body_width/2 + rib_spacing/2 + i * rib_spacing
    rib = Pos(x_pos, -body_height/2 + rib_height/2, -thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    result = result + rib

part = result
part.name = "bracket_with_ribs"
export_step(part, "output.step")