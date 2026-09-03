from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
central_cutout_size = 40.0
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_offset_x = 15.0
hole_offset_y = 10.0
slot_length = 20.0
slot_width = 4.0
slot_offset_y = 25.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

solid_body = solid_body - Box(central_cutout_size, central_cutout_size, plate_thickness * 2)

hole_positions = [
    (-plate_length/2 + hole_offset_x, -plate_width/2 + hole_offset_y),
    ( plate_length/2 - hole_offset_x, -plate_width/2 + hole_offset_y),
    ( plate_length/2 - hole_offset_x,  plate_width/2 - hole_offset_y),
    (-plate_length/2 + hole_offset_x,  plate_width/2 - hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

slot_positions = [(0, -slot_offset_y), (0, slot_offset_y)]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, 0) * Box(slot_length, slot_width, plate_thickness * 2)

part = solid_body
part.name = "plate_with_cutouts"
export_step(part, "output.step")