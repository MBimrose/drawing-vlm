from build123d import *

plate_length = 40.0
plate_width = 12.0
plate_thickness = 4.0
slot_width = 2.0
slot_length = 6.0
slot_offset = 10.0
hole_diameter = 3.3
hole_offset = 30.0

solid = Box(plate_length, plate_width, plate_thickness)

slot_x = -plate_length/2 + slot_offset + slot_width/2
slot_cut = Pos(slot_x, plate_width/2 - slot_length/2, 0) * Box(slot_width, slot_length, plate_thickness)
solid = solid - slot_cut

hole_x = -plate_length/2 + hole_offset
hole_cut = Pos(hole_x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness)
solid = solid - hole_cut

part = solid
part.name = "plate_with_slot_and_hole"
export_step(part, "output.step")