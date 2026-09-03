from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 6.0
opening_width = 32.0
opening_height = 20.0
slot_length = 24.0
slot_width = 5.0
slot_offset_x = -opening_width/2 - slot_width/2 - 2.0
fillet_radius = 2.0

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)
solid_body = solid_body - Box(opening_width, opening_height, plate_thickness)

with BuildPart() as sp:
    with BuildSketch() as s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness)
slot_solid = sp.part
solid_body = solid_body - Pos(slot_offset_x, 0, -plate_thickness/2) * slot_solid

part = solid_body
part.name = "plate_with_opening_and_slot"
export_step(part, "output.step")