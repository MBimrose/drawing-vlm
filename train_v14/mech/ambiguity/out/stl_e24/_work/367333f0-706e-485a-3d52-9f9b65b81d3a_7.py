from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
cutout_width = 40.0
cutout_height = 30.0
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_offset_x = 25.0
hole_offset_y = 20.0
chamfer_size = 0.5
slot_length = 20.0
slot_width = 4.0
slot_offset = 10.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges(), chamfer_size)
solid_body = solid_body - Box(cutout_width, cutout_height, plate_thickness)

slot_y = plate_width / 2 - slot_offset
solid_body = solid_body - Pos(0, slot_y, 0) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - Pos(0, -slot_y, 0) * Box(slot_length, slot_width, plate_thickness)

for x, y in [(hole_offset_x, hole_offset_y), (-hole_offset_x, hole_offset_y),
             (hole_offset_x, -hole_offset_y), (-hole_offset_x, -hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, plate_thickness / 2) * CounterSinkHole(hole_diameter / 2, countersink_diameter / 2, plate_thickness, countersink_angle)

part = solid_body
part.name = "plate_with_cutouts_and_holes"
export_step(part, "output.step")