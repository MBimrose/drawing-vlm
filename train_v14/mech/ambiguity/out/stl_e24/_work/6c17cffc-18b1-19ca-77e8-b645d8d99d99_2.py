from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
rib_width = 8.0
rib_height = 4.0
hole_diameter = 5.5
hole_pattern_radius = 25.0
hole_count = 6
fillet_radius = 1.0
pocket_diameter = 30.0
pocket_depth = 2.0

base = Box(plate_length, plate_width, plate_thickness)
rib1 = Box(rib_width, plate_width - 2 * rib_width, rib_height)
rib2 = Box(plate_length - 2 * rib_width, rib_width, rib_height)

solid_body = base + rib1 + rib2

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter / 2, plate_thickness + 10)

solid_body = solid_body - Pos(0, 0, -plate_thickness / 2 + pocket_depth / 2) * Cylinder(pocket_diameter / 2, pocket_depth)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_ribs_holes_pocket"
export_step(part, "output.step")