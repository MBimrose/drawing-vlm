from build123d import *
import math

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
corner_radius = 5.0
boss_diameter = 30.0
boss_height = 12.0
hole_diameter = 6.0
hole_pattern_radius = 35.0
hole_count = 6
slot_width = 10.0
slot_length = 40.0
slot_offset_y = 30.0
rib_thickness = 3.0
rib_height = 15.0
rib_offset = 20.0
edge_fillet_radius = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_length)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

solid_body = solid_body + Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter / 2, 100)

solid_body = solid_body - Pos(0, slot_offset_y, 0) * Box(slot_width, slot_length, 100)

rib1 = Pos(rib_offset, 0, plate_thickness) * Box(rib_thickness, rib_height, plate_thickness)
rib2 = Pos(-rib_offset, 0, plate_thickness) * Box(rib_thickness, rib_height, plate_thickness)
solid_body = solid_body + rib1 + rib2

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), edge_fillet_radius)

part = solid_body
part.name = "plate_with_boss_holes_slot_ribs"
export_step(part, "output.step")