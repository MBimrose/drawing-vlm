from build123d import *

base_length = 70.0
base_width = 20.0
base_thickness = 10.0
rib_length = 30.0
rib_width = 6.0
rib_height = 10.0
rib_offset1 = 20.0
rib_offset2 = 50.0
slot_width = 4.0
slot_depth = 4.0
slot_cut_depth = 3.0
hole_diameter = 4.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
rib1 = Pos(rib_offset1, base_width/2 + rib_width/2, base_thickness) * Box(rib_length, rib_width, rib_height)
rib2 = Pos(rib_offset2, base_width/2 + rib_width/2, base_thickness) * Box(rib_length, rib_width, rib_height)

solid_body = base + rib1 + rib2

slot = Pos(rib_offset1, base_width/2 + rib_width/2, base_thickness + rib_height - slot_cut_depth/2) * Box(slot_width, slot_depth, slot_cut_depth)
solid_body = solid_body - slot

hole1 = Pos(rib_offset1, 0, base_thickness + rib_height/2) * Cylinder(hole_diameter/2, rib_height)
hole2 = Pos(rib_offset2, 0, base_thickness + rib_height/2) * Cylinder(hole_diameter/2, rib_height)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "ribbed_plate_with_slot_and_holes"
export_step(part, "output.step")