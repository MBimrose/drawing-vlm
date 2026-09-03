from build123d import *
import math

plate_length = 80.0
plate_width = 50.0
plate_thickness = 10.0
slot_length = 30.0
slot_width = 6.0
slot_offset_y = 10.0
hole_diameter = 4.5
hole_head_diameter = 8.6
hole_head_angle = 90
hole_spacing = 50.0
rib_height = 2.0
rib_width = 5.0
rib_spacing = 12.0
chamfer_size = 0.8

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body - Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)

csk_radius = hole_head_diameter / 2
csk_height = csk_radius / math.tan(math.radians(hole_head_angle / 2))
hole_radius = hole_diameter / 2

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_radius, plate_thickness)
    solid_body = solid_body - Pos(x, 0, -plate_thickness/2 + csk_height/2) * Cone(csk_radius, 0, csk_height)

rib_count = int((plate_length - 2 * rib_spacing) // rib_spacing) + 1
for i in range(rib_count):
    x = -plate_length/2 + rib_spacing + i * rib_spacing
    solid_body = solid_body + Pos(x, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width - 2 * rib_spacing, rib_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")