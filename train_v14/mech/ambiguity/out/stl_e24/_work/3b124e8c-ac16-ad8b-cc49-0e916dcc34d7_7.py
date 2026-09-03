from build123d import *

plate_width = 90.0
plate_depth = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
groove_diameter = 20.0
groove_depth = 2.0
pocket_width = 20.0
pocket_depth = 20.0
pocket_depth_cut = 4.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
slot_width = 10.0
slot_length = 30.0
chamfer_size = 0.8

result = Box(plate_width, plate_depth, plate_thickness)
result = result + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result - Pos(0, 0, plate_thickness/2 + boss_height - groove_depth/2) * Cylinder(groove_diameter/2, groove_depth)
result = result - Pos(0, 0, plate_thickness/2 + boss_height - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
result = result - Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(mount_hole_diameter/2, boss_height + 0.1)

hole_positions = [
    (-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_depth/2 - mount_hole_offset),
    (plate_width/2 - mount_hole_offset, plate_depth/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 0.1)

result = result - Pos(-plate_width/2 + plate_thickness/2, 0, 0) * Box(plate_thickness, slot_width, slot_length)
result = result - Pos(plate_width/2 - plate_thickness/2, 0, 0) * Box(plate_thickness, slot_width, slot_length)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_slots"
export_step(part, "output.step")