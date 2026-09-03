from build123d import *
import math

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
corner_radius = 5.0
boss_diameter = 30.0
boss_height = 10.0
hole_diameter = 6.0
hole_pattern_radius = 35.0
hole_count = 6
rib_thickness = 3.0
rib_length = 10.0
rib_height = 5.0
rib_offset = 20.0
fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_length)
    extrude(amount=plate_thickness)
base = p.part
base = fillet(base.edges().filter_by(Axis.Z), corner_radius)

boss = Pos(0, 0, plate_thickness) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

rib1 = Pos(0, rib_offset, plate_thickness) * Box(rib_length, rib_thickness, rib_height)
rib2 = Pos(rib_offset, 0, plate_thickness) * Box(rib_thickness, rib_length, rib_height)
result = result + rib1 + rib2

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(hole_diameter/2, 100)

result = fillet(result.edges().filter_by(Axis.Z), fillet_radius)

part = result
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")