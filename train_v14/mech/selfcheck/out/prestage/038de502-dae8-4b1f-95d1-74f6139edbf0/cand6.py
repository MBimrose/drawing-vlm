from build123d import *
import math

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 5.0
corner_fillet = 4.0
slot_length = 40.0
slot_width = 15.0
hole_diameter = 5.0
hole_radius = hole_diameter / 2.0
hole_circle_radius = 30.0
hole_count = 8

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet)

slot = Box(slot_length, slot_width, plate_thickness * 2)
solid_body = solid_body - slot

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_radius, plate_thickness * 2)

part = solid_body
part.name = "plate_with_slot_and_holes"
export_step(part, "output.step")