from build123d import *
import math

plate_width = 80.0
plate_height = 60.0
plate_thickness = 4.0
slot_width = 8.0
slot_length = 30.0
slot_offset_y = 15.0
boss_diameter = 30.0
boss_height = 2.0
hole_diameter = 4.0
hole_pattern_radius = 20.0
chamfer_size = 0.4
rib_width = 5.0
rib_height = 15.0
rib_offset = 10.0

result = Box(plate_width, plate_height, plate_thickness)
result = result + Cylinder(boss_diameter/2, boss_height)

with BuildPart() as sp:
    with BuildSketch() as s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 10)
slot_solid = sp.part

result = result - Pos(0, slot_offset_y, 0) * slot_solid
result = result - Pos(0, -slot_offset_y, 0) * slot_solid

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    result = result - Pos(px, py, 0) * Cylinder(hole_diameter/2, plate_thickness + 10)

rib1 = Pos(-plate_width/2 + rib_offset, 0, 0) * Box(rib_width, rib_height, plate_thickness)
rib2 = Pos(plate_width/2 - rib_offset, 0, 0) * Box(rib_width, rib_height, plate_thickness)
result = result + rib1 + rib2

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "plate_with_boss_slots_holes_ribs"
export_step(part, "output.step")