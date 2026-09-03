from build123d import *
import math

plate_length = 80.0
plate_width = 40.0
plate_thickness = 8.0
central_hole_dia = 20.0
countersink_dia = 10.0
countersink_angle = 82.0
countersink_depth = 6.0
slot_width = 8.0
slot_length = 20.0
mount_hole_dia = 4.0
mount_hole_offset = 12.0
rib_width = 6.0
rib_length = 20.0
rib_height = 4.0
chamfer_size = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

solid_body = solid_body - Cylinder(central_hole_dia/2, plate_thickness)

csk_radius = countersink_dia / 2
csk_top_radius = csk_radius + countersink_depth * math.tan(math.radians(countersink_angle / 2))
solid_body = solid_body - Pos(0, 0, plate_thickness/2 - countersink_depth/2) * Cone(csk_radius, csk_top_radius, countersink_depth)

solid_body = solid_body - Pos(-plate_length/2 + slot_length/2, 0, 0) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - Pos(plate_length/2 - slot_length/2, 0, 0) * Box(slot_length, slot_width, plate_thickness)

solid_body = solid_body - Pos(0, mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, plate_length)
solid_body = solid_body - Pos(0, -mount_hole_offset, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_dia/2, plate_length)

rib1 = Pos(-plate_length/4, 0, plate_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)
rib2 = Pos(plate_length/4, 0, plate_thickness + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_holes_slots_and_ribs"
export_step(part, "output.step")