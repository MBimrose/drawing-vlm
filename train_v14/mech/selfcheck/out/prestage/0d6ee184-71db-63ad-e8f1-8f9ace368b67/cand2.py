from build123d import *

base_width = 70.0
base_height = 30.0
thickness = 10.0
rib_width = 40.0
rib_height = 12.0
fillet_radius = 2.0
hole_diameter = 5.0
hole_positions = [(-15.0, 0.0), (15.0, 0.0), (0.0, 15.0)]

base = Box(base_width, base_height, thickness)
rib = Pos(0, base_height/2 + rib_height/2, 0) * Box(rib_width, rib_height, thickness)
solid_body = base + rib

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, thickness * 2)

part = solid_body
part.name = "base_with_rib_and_holes"
export_step(part, "output.step")