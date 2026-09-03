from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 4.0
slot_length = 30.0
slot_width = 8.0
slot_offset_y = 15.0
hole_diameter = 4.0
hole_pattern_radius = 20.0
hole_count = 6
chamfer_distance = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2, both=True)
slot_solid = slot_bp.part

solid_body = solid_body - Pos(0, slot_offset_y, 0) * slot_solid
solid_body = solid_body - Pos(0, -slot_offset_y, 0) * slot_solid

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

solid_body = chamfer(solid_body.edges(), chamfer_distance)

part = solid_body
part.name = "plate_with_slots_and_holes"
export_step(part, "output.step")