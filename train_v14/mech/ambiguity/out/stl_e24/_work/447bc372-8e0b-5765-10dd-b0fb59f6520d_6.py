from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 10.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 4.0
hole_diameter = 6.0
hole_count = 6
hole_radius = (inner_diameter/2 + outer_diameter/2) / 2
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter/2)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(inner_diameter/2, thickness * 2)
solid_body = solid_body - Pos(0, 0, thickness - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness/2) * Cylinder(hole_diameter/2, thickness * 2)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "ring_with_pocket_and_holes"
export_step(part, "output.step")