from build123d import *
import math

outer_radius = 15.0
inner_radius = 10.0
thickness = 5.0
lobe_offset = 30.0
fillet_radius = 2.0

lobes = [(0, 0), (lobe_offset, 0), (-lobe_offset, 0)]

solid_body = None
for x, y in lobes:
    lobe = Pos(x, y, 0) * Cylinder(outer_radius, thickness)
    if solid_body is None:
        solid_body = lobe
    else:
        solid_body = solid_body + lobe

solid_body = fillet(solid_body.edges(), fillet_radius)

for x, y in lobes:
    hole = Pos(x, y, 0) * Cylinder(inner_radius, thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "lobed_disc"
export_step(part, "output.step")