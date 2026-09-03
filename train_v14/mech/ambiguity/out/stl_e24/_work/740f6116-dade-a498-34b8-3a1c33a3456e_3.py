from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 8.0
slot_length = 50.0
slot_width = 4.0
slot_spacing = 20.0
chamfer_size = 0.8
mount_hole_dia = 5.0
mount_hole_offset = 10.0

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = base + boss

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 10)
slot_solid = slot_bp.part

result = result - Pos(0, slot_spacing/2, 0) * slot_solid
result = result - Pos(0, -slot_spacing, 0) * slot_solid

hole_positions = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_dia/2, plate_thickness + 10)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "plate_with_boss_slots_holes"
export_step(part, "output.step")