from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 8.0
slot_length = 50.0
slot_width = 4.0
slot_spacing = 30.0
mount_hole_diameter = 5.0
mount_hole_offset = 10.0
chamfer_size = 0.8

result = Box(plate_length, plate_width, plate_thickness)

for x, y in [(-plate_length/2 + mount_hole_offset, -plate_width/4),
             (-plate_length/2 + mount_hole_offset,  plate_width/4),
             ( plate_length/2 - mount_hole_offset, -plate_width/4),
             ( plate_length/2 - mount_hole_offset,  plate_width/4)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 1)
slot_solid = slot_bp.part

for y in [-slot_spacing/2, slot_spacing/2]:
    result = result - Pos(0, y, -plate_thickness/2) * slot_solid

result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_slots_and_holes"
export_step(part, "output.step")