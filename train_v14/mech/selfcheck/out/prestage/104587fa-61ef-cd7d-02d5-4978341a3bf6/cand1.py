from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 5.0
hole_diameter = 4.0
hole_depth = 2.0
hole_count = 12
hole_circle_radius = (inner_diameter/2 + outer_diameter/2) / 2

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter/2)
        Circle(inner_diameter/2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part
for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

part = solid_body
part.name = "washer_with_holes"
export_step(part, "output.step")