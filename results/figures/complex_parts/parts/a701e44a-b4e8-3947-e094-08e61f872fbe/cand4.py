from build123d import *

bracket_width = 80.0
bracket_height = 40.0
bracket_thickness = 8.0
leg_height = 30.0
leg_thickness = 8.0
fillet_radius = 4.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 6.0
hole_diameter = 6.0
hole_spacing = 30.0
rib_width = 5.0
rib_height = 12.0
rib_thickness = 2.0
rib_spacing = 8.0

base = Box(bracket_width, bracket_height, bracket_thickness)
leg = Pos(bracket_width/2 - leg_thickness/2, bracket_height/2 + leg_height/2, 0) * Box(leg_thickness, leg_height, bracket_thickness)
result = base + leg

z_edges = result.edges().filter_by(Axis.Z)
max_x = max(e.center().X for e in z_edges)
x_edges = [e for e in z_edges if abs(e.center().X - max_x) < 0.1]
result = fillet(x_edges, fillet_radius)

pocket = Pos(0, 0, bracket_thickness/2 - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)
result = result - pocket

hole_center_x = bracket_width/2 - leg_thickness/2
hole_center_y = bracket_height/2 + leg_height/2
for dy in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(hole_center_x, hole_center_y + dy, 0) * Cylinder(hole_diameter/2, bracket_thickness + 2)
    result = result - hole

rib_count = int((bracket_width - 2 * rib_spacing) // (rib_width + rib_spacing))
for i in range(rib_count):
    x_pos = -bracket_width/2 + rib_spacing + i * (rib_width + rib_spacing) + rib_width/2
    rib = Pos(x_pos, -bracket_height/2 + rib_height/2, -bracket_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
    result = result + rib

part = result
part.name = "bracket"
export_step(part, "output.step")