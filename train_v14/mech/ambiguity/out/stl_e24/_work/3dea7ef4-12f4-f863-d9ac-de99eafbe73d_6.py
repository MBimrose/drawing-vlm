from build123d import *
import math

plate_width = 80.0
plate_height = 100.0
plate_thickness = 5.0
corner_radius = 5.0
boss_diameter = 30.0
boss_height = 10.0
hole_diameter = 6.0
hole_count = 6
hole_circle_radius = 35.0
fillet_radius = 1.0
rib_width = 10.0
rib_height = 15.0
rib_thickness = 4.0
slot_width = 12.0
slot_height = 4.0
slot_offset_y = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_radius)

solid_body = solid_body + Pos(0, 0, plate_thickness) * Cylinder(boss_diameter / 2, boss_height)

rib = Pos(boss_diameter / 2 + rib_width / 2, 0, plate_thickness) * Box(rib_thickness, rib_height, rib_width)
solid_body = solid_body + rib

slot = Pos(0, slot_offset_y, plate_thickness / 2) * Box(slot_width, slot_height, plate_thickness)
solid_body = solid_body - slot

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_boss_rib_holes"
export_step(part, "output.step")