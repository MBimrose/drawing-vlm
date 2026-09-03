from build123d import *

width = 40.0
depth = 12.0
thickness = 4.0
slot_width = 2.0
slot_length = 6.0
slot_offset = 4.0
hole_diameter = 3.3
hole_offset = 30.0
rib_width = 6.0
rib_height = 2.0
rib_thickness = 1.5
chamfer = 0.5

solid_body = Pos(0.5 * width, 0, 0.5 * thickness) * Box(width, depth, thickness)

slot_center_x = slot_offset + 0.5 * slot_width
slot_cut = Pos(slot_center_x, 0.5 * depth - 0.5 * slot_length, 0.5 * thickness) * Box(slot_width, slot_length, thickness)
solid_body = solid_body - slot_cut

hole_center_x = hole_offset
hole_cut = Pos(hole_center_x, 0, 0.5 * thickness) * Cylinder(hole_diameter / 2, thickness)
solid_body = solid_body - hole_cut

rib = Pos(0.5 * width, 0, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_slot_hole_rib"
export_step(part, "output.step")