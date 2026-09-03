from build123d import *
import math

plate_length = 80.0
plate_width = 80.0
plate_thickness = 5.0
corner_fillet = 4.0
slot_length = 40.0
slot_width = 15.0
hole_diameter = 5.0
hole_count = 8
hole_pattern_radius = 30.0
rib_width = 20.0
rib_length = 40.0
rib_height = 3.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet)

slot = Box(slot_length, slot_width, plate_thickness * 2)
solid_body = solid_body - slot

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

rib = Pos(0, 0, -plate_thickness / 2 + rib_height / 2) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_slot_holes_and_rib"
export_step(part, "output.step")