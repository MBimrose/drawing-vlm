from build123d import *

outer_width = 60.0
outer_height = 40.0
length = 80.0
wall_thickness = 4.0
rib_width = 30.0
rib_height = 20.0
rib_thickness = 6.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_count = 3
hole_offset = 10.0

base = Box(outer_width, outer_height, length)
inner = Box(outer_width - 2*wall_thickness, outer_height - 2*wall_thickness, length - 2*wall_thickness)
hollow = base - inner

rib = Pos(0, 0, -length/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
combined = hollow + rib

hole_tool = Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_width + 20)
for i in range(hole_count):
    y = -length/2 + hole_offset + i * hole_spacing
    combined = combined - Pos(outer_width/2, y, -length/2 + hole_offset) * hole_tool
    combined = combined - Pos(-outer_width/2, y, -length/2 + hole_offset) * hole_tool

part = combined
part.name = "hollow_box_with_rib_and_holes"
export_step(part, "output.step")