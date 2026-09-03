from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 8.0
depth = 12.0
fillet_radius = 4.0
pocket_diameter = 20.0
pocket_depth = 6.0
hole_diameter = 6.0
hole_spacing = 20.0

horizontal = Pos(leg_length/2, thickness/2, depth/2) * Box(leg_length, thickness, depth)
vertical = Pos(thickness/2, leg_height/2, depth/2) * Box(thickness, leg_height, depth)
result = horizontal + vertical

inner_edges = [e for e in result.edges() if abs(e.center().X - thickness) < 0.1 and abs(e.center().Y - thickness) < 0.1]
result = fillet(inner_edges, fillet_radius)

pocket = Pos(leg_length/2, thickness/2, depth - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)
result = result - pocket

for i in range(3):
    y = leg_height/2 + (i - 1) * hole_spacing
    hole = Pos(thickness/2, y, depth/2) * Cylinder(hole_diameter/2, depth)
    result = result - hole

part = result
part.name = "L_Bracket"
export_step(part, "output.step")