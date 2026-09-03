from build123d import *

channel_length = 100.0
channel_width = 50.0
channel_height = 30.0
wall_thickness = 2.0
slot_width = 12.0
slot_depth = 4.0
slot_length = channel_length * 0.6
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

inner_width = channel_width - 2 * wall_thickness
inner_height = channel_height - wall_thickness

outer = Pos(0, 0, channel_height / 2) * Box(channel_length, channel_width, channel_height)
inner = Pos(0, 0, wall_thickness + inner_height / 2) * Box(inner_width, inner_height, inner_height)
base = outer - inner

slot = Pos(0, 0, channel_height - slot_depth / 2) * Box(slot_length, slot_width, slot_depth)
base = base - slot

for x in [-hole_spacing, 0, hole_spacing]:
    base = base - Pos(x, 0, channel_height / 2) * Cylinder(hole_diameter / 2, channel_height + 10)

top_edges = base.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
base = chamfer(top_edges, chamfer_size)

part = base
part.name = "channel_with_slot_and_holes"
export_step(part, "output.step")