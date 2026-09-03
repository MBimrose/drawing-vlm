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
hole_count = 6
rib_thickness = 3.0
rib_width = 15.0
rib_offset = 20.0
rib_fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_length)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)

solid_body = solid_body + Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter / 2, plate_thickness + boss_height + 10)

rib1 = Pos(rib_offset, 0, plate_thickness + plate_thickness / 2) * Box(rib_thickness, rib_width, plate_thickness)
rib2 = Pos(0, rib_offset, plate_thickness + plate_thickness / 2) * Box(rib_width, rib_thickness, plate_thickness)
solid_body = solid_body + rib1 + rib2

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), rib_fillet_radius)

part = solid_body
part.name = "plate_with_boss_and_ribs"
export_step(part, "output.step")