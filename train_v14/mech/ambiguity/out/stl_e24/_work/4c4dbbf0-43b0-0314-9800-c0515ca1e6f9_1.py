from build123d import *

outer_width = 60.0
outer_height = 40.0
length = 80.0
wall_thickness = 4.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset = 10.0

outer = Box(outer_width, outer_height, length)
inner = Box(outer_width - 2*wall_thickness, outer_height - 2*wall_thickness, length - 2*wall_thickness)
channel = outer - inner

hole_r = hole_diameter / 2
hole_tool = Rot(0, 90, 0) * Cylinder(hole_r, outer_width + 10)
for y in [-hole_spacing, 0, hole_spacing]:
    z = -length/2 + hole_offset
    channel = channel - Pos(outer_width/2, y, z) * hole_tool
    channel = channel - Pos(-outer_width/2, y, z) * hole_tool

part = channel
part.name = "channel_with_holes"
export_step(part, "output.step")