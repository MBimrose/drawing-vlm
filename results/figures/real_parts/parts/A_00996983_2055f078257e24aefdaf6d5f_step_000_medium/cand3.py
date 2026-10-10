from build123d import *
import math

gear_teeth = 12
gear_root_radius = 30.0
gear_tip_radius = 35.0
gear_height = 25.0
hex_radius = 20.0
hex_height = 30.0
chamfer_size = 2.0

points = []
for i in range(gear_teeth * 2):
    angle = i * math.pi / gear_teeth
    radius = gear_tip_radius if i % 2 == 0 else gear_root_radius
    points.append((radius * math.cos(angle), radius * math.sin(angle)))

with BuildPart() as p:
    with BuildSketch() as s:
        Polygon(*points)
    extrude(amount=gear_height)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

with BuildPart() as hex_p:
    with BuildSketch(Plane.XY.offset(gear_height)) as hs:
        RegularPolygon(hex_radius * 2, 6)
    extrude(amount=hex_height)

solid_body = solid_body + hex_p.part

part = solid_body
part.name = "gear_with_hex"
export_step(part, "output.step")