from build123d import *

rail_length = 100.0
rail_width = 50.0
rail_height = 30.0
wall_thickness = 3.0
channel_width = 20.0
channel_depth = 12.0
rib_height = 2.0
rib_width = 8.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

base = Pos(0, 0, rail_height/2) * Box(rail_length, rail_width, rail_height)

channel_cut = Pos(0, 0, (rail_height - channel_depth)/2) * Box(channel_width, rail_width, rail_height - channel_depth)
base = base - channel_cut

rib = Pos(0, 0, wall_thickness + rib_height/2) * Box(rail_length, rib_width, rib_height)
base = base + rib

hole_positions = [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]
for x, y in hole_positions:
    base = base - Pos(x, y, rail_height/2) * Cylinder(hole_diameter/2, rail_height)

chamfer_edges = base.edges().filter_by(Axis.Z).sort_by(Axis.X)[-2:]
base = chamfer(chamfer_edges, chamfer_size)

part = base
part.name = "rail_with_channel_and_rib"
export_step(part, "output.step")