from build123d import *
import math

outer_radius = 15.0
inner_radius = 10.0
thickness = 5.0
lobe_offset = 25.0
fillet_radius = 2.0
central_pocket_radius = 12.0
central_pocket_depth = 2.0

lobe_positions = [
    (0, lobe_offset),
    (-lobe_offset * math.cos(math.radians(30)), -lobe_offset * math.sin(math.radians(30))),
    (lobe_offset * math.cos(math.radians(30)), -lobe_offset * math.sin(math.radians(30)))
]

solid_body = Cylinder(outer_radius, thickness)
for x, y in lobe_positions:
    solid_body = solid_body + Pos(x, y, 0) * Cylinder(outer_radius, thickness)

solid_body = fillet(solid_body.edges(), fillet_radius)

hole_positions = [(0, 0)] + lobe_positions
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(inner_radius, thickness)

solid_body = solid_body - Pos(0, 0, thickness/2 - central_pocket_depth/2) * Cylinder(central_pocket_radius, central_pocket_depth)

part = solid_body
part.name = "multi_lobe_disc"
export_step(part, "output.step")