from build123d import *

base_radius = 30.0
base_height = 25.0
rib_width = 5.0
rib_count = 12
hex_radius = 30.0
hex_height = 30.0
chamfer_size = 2.0

import math

base = Pos(0, 0, base_height / 2) * Cylinder(base_radius, base_height)

rib = Pos(base_radius + rib_width / 2, 0, base_height / 2) * Box(rib_width, base_height, base_height)

ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

base_with_ribs = base + ribs

with BuildPart() as p:
    with BuildSketch(Plane.XY.offset(base_height)) as s:
        RegularPolygon(hex_radius, 6)
    extrude(amount=hex_height)
hex_section = p.part

result = base_with_ribs + hex_section

bottom_face = result.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
result = chamfer(bottom_edges, chamfer_size)

part = result
part.name = "ribbed_base_with_hex"
export_step(part, "output.step")