from build123d import *

rail_length = 80.0
rail_width = 20.0
rail_height = 10.0
rib_width = 10.0
rib_height = 5.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_size = 0.5

base = Box(rail_length, rail_width, rail_height)
rib = Pos(0, 0, rail_height/2 - rib_height/2) * Box(rail_length, rib_width, rib_height)
solid_body = base + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, rail_height + rib_height + 10)

x_edges = solid_body.edges().filter_by(Axis.X)
solid_body = chamfer(x_edges, chamfer_size)

part = solid_body
part.name = "rail_with_rib"
export_step(part, "output.step")