from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 10.0
fillet_radius = 2.0
blind_hole_diameter = 6.0
blind_hole_depth = 6.0
hole_pattern_radius = (inner_diameter/2 + outer_diameter/2) / 2
central_pocket_diameter = 20.0
central_pocket_depth = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter/2)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, thickness/2) * Cylinder(inner_diameter/2, thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, thickness - central_pocket_depth/2) * Cylinder(central_pocket_diameter/2, central_pocket_depth)

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth)

part = solid_body
part.name = "washer_with_holes"
export_step(part, "output.step")