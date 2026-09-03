from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 8.0
slot_length = 50.0
slot_width = 4.0
slot_offset_y = 15.0
hole_diameter = 5.0
hole_offset = 10.0
chamfer_size = 0.8

base = Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

with BuildPart() as sp:
    with BuildSketch() as s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 1)
slot_tool = sp.part

result = result - Pos(0, slot_offset_y, -plate_thickness/2) * slot_tool
result = result - Pos(0, -2*slot_offset_y, -plate_thickness/2) * slot_tool

hole_tool = Cylinder(hole_diameter/2, plate_thickness + 1)
for x, y in [(plate_length/2 - hole_offset, plate_width/2 - hole_offset),
             (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
             (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
             (plate_length/2 - hole_offset, -plate_width/2 + hole_offset)]:
    result = result - Pos(x, y, 0) * hole_tool

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_slots_holes"
export_step(part, "output.step")