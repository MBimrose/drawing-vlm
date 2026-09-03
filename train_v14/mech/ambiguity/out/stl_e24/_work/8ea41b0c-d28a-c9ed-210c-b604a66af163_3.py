from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
slot_width = 12.0
slot_length = 30.0
hole_diameter = 6.0
hole_pattern_radius = 20.0
rib_height = 10.0
rib_width = 8.0
rib_thickness = 2.0
notch_width = 15.0
notch_depth = 10.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

# Slot cut through center
solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)

# 3 holes in polar array
for i in range(3):
    angle = math.radians(i * 120)
    hx = hole_pattern_radius * math.cos(angle)
    hy = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(hx, hy, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

# Notch at top-right corner
notch_x = plate_length/2 - notch_depth/2
notch_y = plate_width/2 - notch_width/2
solid_body = solid_body - Pos(notch_x, notch_y, plate_thickness/2) * Box(notch_depth, notch_width, plate_thickness)

# Ribs on bottom face
rib1 = Pos(-plate_length/2 + rib_width/2, 0, -rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
rib2 = Pos(plate_length/2 - rib_width/2, 0, -rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_slot_holes_notch_ribs"
export_step(part, "output.step")