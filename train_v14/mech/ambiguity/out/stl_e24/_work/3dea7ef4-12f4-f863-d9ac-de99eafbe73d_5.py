from build123d import *
import math

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
corner_fillet_radius = 5.0
boss_diameter = 30.0
boss_height = 10.0
hole_diameter = 6.0
hole_pattern_radius = 35.0
rib_width = 10.0
rib_height = 15.0
rib_thickness = 4.0
rib_spacing = 20.0
edge_fillet_radius = 1.0

base = Pos(0, 0, plate_thickness / 2) * Box(plate_width, plate_length, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_fillet_radius)

boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)
result = base + boss

rib1 = Pos(rib_spacing / 2, 0, plate_thickness) * Box(rib_thickness, rib_height, rib_width)
rib2 = Pos(0, rib_spacing, plate_thickness) * Box(rib_width, rib_thickness, rib_height)
result = result + rib1 + rib2

result = fillet(result.edges().filter_by(Axis.Z), edge_fillet_radius)

for i in range(6):
    angle = math.radians(i * 360.0 / 6)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(hole_diameter / 2, 200)

part = result
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")