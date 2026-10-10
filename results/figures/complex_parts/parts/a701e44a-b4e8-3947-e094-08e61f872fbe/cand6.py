from build123d import *

leg_length_long = 80.0
leg_length_short = 50.0
leg_width = 20.0
thickness = 8.0
fillet_radius = 4.0
chamfer_distance = 1.0
pocket_length = 30.0
pocket_width = 12.0
pocket_depth = 6.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_from_inner = 15.0

long_leg = Box(leg_length_long, leg_width, thickness)
short_leg = Pos(leg_length_long/2 - leg_width/2, leg_length_short/2, 0) * Box(leg_width, leg_length_short, thickness)
result = long_leg + short_leg

z_edges = result.edges().filter_by(Axis.Z)
short_leg_edges = [e for e in z_edges if e.center().X > 0]
result = fillet(short_leg_edges, fillet_radius)

z_edges = result.edges().filter_by(Axis.Z)
long_leg_edges = [e for e in z_edges if e.center().X < 0]
result = chamfer(long_leg_edges, chamfer_distance)

pocket1 = Pos(-leg_length_long/4, 0, thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket1

pocket2 = Pos(leg_length_long/4, leg_length_short/2, thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket2

for i in range(2):
    hx = leg_length_long/2 - leg_width/2
    hy = hole_offset_from_inner + i * hole_spacing
    hole = Pos(hx, hy, thickness/2) * Cylinder(hole_diameter/2, thickness)
    result = result - hole

part = result
part.name = "L_bracket"
export_step(part, "output.step")