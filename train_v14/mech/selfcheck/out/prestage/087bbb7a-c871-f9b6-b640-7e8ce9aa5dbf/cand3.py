from build123d import *

rail_length = 100.0
rail_width = 30.0
rail_height = 20.0
wall_thickness = 2.0
rib_width = 6.0
rib_height = 4.0
fillet_radius = 1.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 4

inner_width = rail_width - 2 * wall_thickness
inner_height = rail_height - 2 * wall_thickness

outer = Box(rail_length, rail_width, rail_height)
inner = Box(rail_length, inner_width, inner_height)
base = outer - inner

rib = Pos(0, 0, -rail_height/2 + wall_thickness + rib_height/2) * Box(rail_length, rib_width, rib_height)
combined = base + rib

x_edges = combined.edges().filter_by(Axis.X)
combined = fillet(x_edges, fillet_radius)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    hole = Pos(x, rail_width/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, rail_width + 10)
    combined = combined - hole

part = combined
part.name = "rail_with_rib_and_holes"
export_step(part, "output.step")