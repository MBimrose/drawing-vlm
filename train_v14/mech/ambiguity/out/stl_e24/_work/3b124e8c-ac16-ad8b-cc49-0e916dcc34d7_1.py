from build123d import *

plate_width = 90.0
plate_depth = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
pocket_width = 20.0
pocket_depth = 20.0
pocket_depth_cut = 4.0
central_hole_diameter = 5.0
mount_hole_diameter = 5.0
mount_hole_offset = 12.0
slot_width = 10.0
slot_length = 30.0
chamfer_size = 0.8

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(central_hole_diameter/2, plate_thickness + boss_height + 1)

for x, y in [(-plate_width/2 + mount_hole_offset, -plate_depth/2 + mount_hole_offset),
             (plate_width/2 - mount_hole_offset, -plate_depth/2 + mount_hole_offset),
             (-plate_width/2 + mount_hole_offset, plate_depth/2 - mount_hole_offset),
             (plate_width/2 - mount_hole_offset, plate_depth/2 - mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

for x in [-plate_width/2 + slot_width/2, plate_width/2 - slot_width/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Box(slot_length, slot_width, plate_thickness + 1)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_boss_pockets_and_slots"
export_step(part, "output.step")