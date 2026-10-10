from build123d import *

lever_length = 80.0
lever_width = 10.0
lever_thickness = 6.0
slot_start_width = 8.0
slot_end_width = 4.0
slot_length = 40.0
slot_depth = 4.0
slot_offset = 30.0
boss_diameter = 12.0
boss_length = 20.0
hole_diameter = 4.0
hole_offset = 20.0
chamfer_size = 0.5

base = Pos(lever_length/2, 0, lever_thickness/2) * Box(lever_length, lever_width, lever_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        with BuildLine() as slot_line:
            Polyline((slot_offset, -slot_start_width/2), (slot_offset + slot_length, -slot_end_width/2),
                     (slot_offset + slot_length, slot_end_width/2), (slot_offset, slot_start_width/2), close=True)
        make_face()
    extrude(amount=slot_depth)
slot_solid = slot_bp.part

result = base - slot_solid

boss = Pos(lever_length + boss_length/2, 0, lever_thickness/2) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_length)
result = result + boss

for x, y in [(hole_offset, 0), (lever_length - hole_offset, 0)]:
    result = result - Pos(x, y, lever_thickness/2) * Cylinder(hole_diameter/2, lever_thickness + 2)

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "lever_with_slot_and_boss"
export_step(part, "output.step")