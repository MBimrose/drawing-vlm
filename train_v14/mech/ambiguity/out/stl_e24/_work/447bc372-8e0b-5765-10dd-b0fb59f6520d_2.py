from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
thickness = 10.0
pocket_diameter = 20.0
pocket_depth = 4.0
blind_hole_diameter = 6.0
blind_hole_depth = 6.0
blind_hole_count = 6
fillet_radius = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
pocket_radius = pocket_diameter / 2.0
blind_hole_radius = blind_hole_diameter / 2.0
hole_pattern_radius = (inner_radius + outer_radius) / 2.0

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(inner_radius, thickness)
solid_body = solid_body - Pos(0, 0, thickness - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)

for i in range(blind_hole_count):
    angle = math.radians(i * 360.0 / blind_hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, thickness / 2 - blind_hole_depth / 2) * Cylinder(blind_hole_radius, blind_hole_depth)

solid_body = fillet(solid_body.edges(), fillet_radius)

part = solid_body
part.name = "washer_with_pocket_and_holes"
export_step(part, "output.step")