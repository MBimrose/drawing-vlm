from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
plate_chamfer = 1.0
slot_width = 20.0
slot_height = 2.0
slot_offset_y = 15.0
slot_depth = 2.5

solid_body = Box(plate_width, plate_height, plate_thickness)
bottom_face = solid_body.faces().sort_by(Axis.Y)[0]
solid_body = chamfer(bottom_face.edges(), plate_chamfer)
slot = Pos(0, slot_offset_y, plate_thickness/2 - slot_depth/2) * Box(slot_width, slot_height, slot_depth)
solid_body = solid_body - slot

part = solid_body
part.name = "plate_with_slot"
export_step(part, "output.step")