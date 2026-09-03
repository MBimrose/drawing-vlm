from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 10.0
fillet_radius = 2.0
hole_diameter = 6.0
hole_depth = 6.0
hole_count = 6
hole_circle_radius = (outer_diameter / 2) - 10.0
pocket_diameter = 20.0
pocket_depth = 4.0
rib_width = 5.0
rib_height = 3.0
rib_thickness = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Pos(0, 0, thickness / 2) * Cylinder(inner_diameter / 2, thickness)
solid_body = fillet(solid_body.edges(), fillet_radius)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

solid_body = solid_body - Pos(0, 0, thickness - pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)

rib = Pos(inner_diameter / 2 + rib_thickness / 2, 0, thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "flanged_disc_with_rib"
export_step(part, "output.step")