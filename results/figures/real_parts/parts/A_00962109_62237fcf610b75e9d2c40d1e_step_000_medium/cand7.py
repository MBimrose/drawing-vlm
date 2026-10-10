from build123d import *
import math

outer_radius = 15.0
inner_radius = 10.0
lobe_offset = 30.0
thickness = 8.0
fillet_radius = 2.0
hole_diameter = inner_radius * 2 + 1.0
rib_width = 6.0
rib_height = 4.0
pocket_width = 12.0
pocket_depth = 3.0

lobe_positions = [
    (0, 0),
    (lobe_offset, -lobe_offset / 2),
    (-lobe_offset, -lobe_offset / 2),
]

with BuildPart() as p:
    with BuildSketch() as s:
        for x, y in lobe_positions:
            Pos(x, y, 0) * Circle(outer_radius)
    extrude(amount=thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

for x, y in lobe_positions:
    solid_body = solid_body - Pos(x, y, thickness / 2) * Cylinder(hole_diameter / 2, thickness)

solid_body = solid_body + Pos(0, 0, thickness / 2) * Box(rib_width, rib_height, thickness)

solid_body = solid_body - Pos(0, 0, thickness - pocket_depth / 2) * Box(pocket_width, pocket_width, pocket_depth)

part = solid_body
part.name = "multi_lobe_plate"
export_step(part, "output.step")