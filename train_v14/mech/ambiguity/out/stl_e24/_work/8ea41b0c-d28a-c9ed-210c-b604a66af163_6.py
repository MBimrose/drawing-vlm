from build123d import *
import math

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
hole_diameter = 6.0
hole_spacing = 20.0
slot_width = 12.0
slot_length = 30.0
slot_offset_x = 15.0
rib_width = 10.0
rib_height = 10.0
notch_width = 8.0
notch_height = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)

solid_body = p.part

tri_height = hole_spacing * math.sqrt(3) / 2
hole_positions = [
    (-hole_spacing / 2, -tri_height / 3),
    (hole_spacing / 2, -tri_height / 3),
    (0, 2 * tri_height / 3)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

solid_body = solid_body - Pos(slot_offset_x, 0, 0) * Box(slot_width, slot_length, plate_thickness * 2)

rib = Box(rib_width, rib_width, rib_height)
solid_body = solid_body + Pos(plate_width / 2, 0, 0) * rib
solid_body = solid_body + Pos(-plate_width / 2, 0, 0) * rib

solid_body = solid_body - Pos(plate_width / 2 - notch_width / 2, plate_height / 2 - notch_height / 2, 0) * Box(notch_width, notch_height, plate_thickness * 2)

part = solid_body
part.name = "plate_with_holes_slot_ribs_notch"
export_step(part, "output.step")