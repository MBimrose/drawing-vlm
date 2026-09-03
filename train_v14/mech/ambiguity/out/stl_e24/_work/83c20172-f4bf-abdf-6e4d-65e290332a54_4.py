from build123d import *

rail_length = 100.0
rail_width = 50.0
rail_height = 30.0
wall_thickness = 2.0
channel_width = rail_width - 2 * wall_thickness
channel_depth = rail_height - 2 * wall_thickness
slot_width = 2.0
slot_depth = channel_depth - wall_thickness
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

base = Pos(0, 0, rail_height/2) * Box(rail_length, rail_width, rail_height)
channel = Pos(0, 0, rail_height - channel_depth/2) * Box(channel_width, rail_length, channel_depth)
slot = Pos(0, 0, rail_height - channel_depth - slot_depth/2) * Box(slot_width, rail_length, slot_depth)

result = base - channel - slot

for x, y in [(-hole_spacing, 0), (0, 0), (hole_spacing, 0)]:
    result = result - Pos(x, y, rail_height/2) * Cylinder(hole_diameter/2, rail_height)

chamfer_edges = result.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-4:]
result = chamfer(chamfer_edges, chamfer_size)

part = result
part.name = "rail_with_channel"
export_step(part, "output.step")