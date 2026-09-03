from build123d import *
import math

outer_diameter = 80.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 3.0
hole_diameter = 4.0
hole_depth = 2.0
hole_count = 12
hole_ring_radius = 30.0
chamfer_size = 0.5

base = Cylinder(outer_diameter / 2, plate_thickness)
boss = Cylinder(boss_diameter / 2, boss_height)
result = base + boss

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_ring_radius * math.cos(angle)
    py = hole_ring_radius * math.sin(angle)
    result = result - Pos(px, py, plate_thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")