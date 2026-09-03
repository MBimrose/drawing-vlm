from build123d import *
import math

outer_diameter = 80.0
plate_thickness = 5.0
hole_diameter = 4.0
hole_depth = 3.0
hole_count = 12
hole_radius = 30.0

solid_body = Cylinder(outer_diameter / 2, plate_thickness)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_radius * math.cos(angle)
    py = hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "plate_with_polar_holes"
export_step(part, "output.step")