from build123d import *

length = 100.0
width = 50.0
height = 30.0
wall_thickness = 2.0
channel_width = width - 2 * wall_thickness
channel_depth = height - 2 * wall_thickness
rib_thickness = 3.0
rib_height = 10.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

base = Pos(0, 0, height/2) * Box(length, width, height)
channel_cut = Pos(0, 0, height/2) * Box(channel_width, length, channel_depth)
result = base - channel_cut

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(length, rib_thickness, rib_height)
result = result + rib

for x in [-hole_spacing, 0, hole_spacing]:
    result = result - Pos(x, 0, height/2) * Cylinder(hole_diameter/2, height)

top_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-4:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "channel_with_rib"
export_step(part, "output.step")