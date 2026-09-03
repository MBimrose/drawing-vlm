from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 8.0
slot_length = 50.0
slot_width = 4.0
slot_offset_y = 15.0
chamfer_size = 0.8
mount_hole_diameter = 5.0
mount_hole_offset = 10.0

base = Box(plate_width, plate_depth, plate_thickness)
boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = base + boss

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 10)
slot_cutter = slot_bp.part

solid_body = solid_body - Pos(0, -plate_depth/2 + slot_offset_y, -plate_thickness/2) * slot_cutter
solid_body = solid_body - Pos(0, plate_depth/2 - slot_offset_y, -plate_thickness/2) * slot_cutter

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

hole_cutter = Cylinder(mount_hole_diameter/2, plate_thickness + boss_height + 10)
hole_positions = [
    (-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_depth/2 - mount_hole_offset),
    (plate_width/2 - mount_hole_offset, plate_depth/2 - mount_hole_offset),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2 + boss_height/2) * hole_cutter

part = solid_body
part.name = "plate_with_boss_slots_and_holes"
export_step(part, "output.step")