from build123d import *

rail_length = 100.0
rail_width = 30.0
rail_height = 20.0
wall_thickness = 2.0
web_thickness = 6.0
fillet_radius = 1.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 4
hole_offset = 10.0

outer = Box(rail_length, rail_width, rail_height)
inner = Box(rail_length, rail_width - 2 * wall_thickness, rail_height - 2 * wall_thickness)
tube = outer - inner

web = Box(rail_length, web_thickness, rail_height - 2 * wall_thickness)
tube = tube + web

tube = fillet(tube.edges().filter_by(Axis.X), fillet_radius)

for i in range(hole_count):
    x = -rail_length / 2 + hole_offset + i * hole_spacing
    tube = tube - Pos(x, rail_width / 2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, rail_width + 10)

part = tube
part.name = "rail_with_web_and_holes"
export_step(part, "output.step")