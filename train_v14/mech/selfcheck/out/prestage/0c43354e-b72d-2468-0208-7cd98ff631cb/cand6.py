from build123d import *

outer_length = 80.0
outer_width = 30.0
outer_height = 60.0
wall_thickness = 1.0
web_thickness = 2.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_offset_from_end = 12.0
chamfer_distance = 0.05

inner_width = outer_width - 2 * wall_thickness
cavity_height = outer_height - 2 * wall_thickness
cavity_length = outer_length - 2 * wall_thickness
channel_width = (inner_width - web_thickness) / 2.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])

channel1 = Pos(0, -(web_thickness/2 + channel_width/2), outer_height/2) * Box(cavity_length, channel_width, cavity_height)
channel2 = Pos(0, (web_thickness/2 + channel_width/2), outer_height/2) * Box(cavity_length, channel_width, cavity_height)

result = base - channel1 - channel2

for i in range(3):
    x = -outer_length/2 + hole_offset_from_end + i * hole_spacing
    result = result - Pos(x, 0, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "hollow_box_with_channels"
export_step(part, "output.step")