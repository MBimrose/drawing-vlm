from build123d import *

plate_length = 90.0
plate_width = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
blind_hole_diameter = 5.0
blind_hole_depth = 6.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
slot_length = 20.0
slot_width = 8.0
rib_width = 20.0
rib_length = 30.0
rib_height = 4.0
chamfer_size = 0.8

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
boss = Pos(0, 0, plate_thickness + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
rib = Pos(0, 0, rib_height/2) * Box(rib_width, rib_length, rib_height)
result = base + boss + rib

blind_hole = Pos(0, 0, plate_thickness + boss_height - blind_hole_depth/2) * Cylinder(blind_hole_diameter/2, blind_hole_depth + 0.1)
result = result - blind_hole

mount_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    ( plate_length/2 - mount_hole_offset,  plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset,  plate_width/2 - mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_thickness + 0.1)

slot1 = Pos(-plate_length/2 + slot_length/2, 0, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness + 0.1)
slot2 = Pos(plate_length/2 - slot_length/2, 0, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness + 0.1)
result = result - slot1 - slot2

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_rib_holes_slots"
export_step(part, "output.step")