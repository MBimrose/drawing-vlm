from build123d import *
import math

outer_radius = 15.0
inner_radius = 10.0
thickness = 5.0
lobe_offset = 20.0
fillet_radius = 2.0

lobes = [(0, lobe_offset), (-lobe_offset, -lobe_offset/2), (lobe_offset, -lobe_offset/2)]

solid_body = Cylinder(outer_radius, thickness)
for x, y in lobes:
    solid_body = solid_body + Pos(x, y, 0) * Cylinder(outer_radius, thickness)

solid_body = fillet(solid_body.edges(), fillet_radius)

for x, y in lobes:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(inner_radius, thickness)

part = solid_body
part.name = "lobed_disc"
export_step(part, "output.step")