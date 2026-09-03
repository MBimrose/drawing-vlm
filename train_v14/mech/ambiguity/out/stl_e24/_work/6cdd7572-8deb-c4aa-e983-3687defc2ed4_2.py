from build123d import *

plate_length = 40.0
plate_width = 12.0
plate_thickness = 4.0
slot_width = 2.0
slot_length = 6.0
slot_offset = 12.0
hole_diameter = 3.3
hole_offset = 10.0
chamfer_dist = 0.2
rib_width = 4.0
rib_height = 2.0
rib_thickness = 1.0

solid_body = Box(plate_length, plate_width, plate_thickness)

slot1 = Pos(-slot_offset, plate_width/2 - slot_length/2, 0) * Box(slot_width, slot_length, plate_thickness)
slot2 = Pos(2*slot_offset, 0, 0) * Box(slot_width, slot_length, plate_thickness)
solid_body = solid_body - slot1 - slot2

hole = Pos(hole_offset, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)
solid_body = solid_body - hole

rib = Pos(-plate_length/2 + rib_width/2, 0, -plate_thickness/2 + rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

part = solid_body
part.name = "plate_with_slots_hole_rib"
export_step(part, "output.step")