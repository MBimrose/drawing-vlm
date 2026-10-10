from build123d import *

plate_width = 80.0
plate_height = 100.0
plate_thickness = 5.0
slot_width = 30.0
slot_height = 60.0
slot_offset_y = 30.0
boss_radius = 12.0
boss_height = 12.0
counterbore_diameter = 8.0
counterbore_cbore_diameter = 14.0
counterbore_cbore_depth = 2.5
mount_hole_diameter = 5.0
mount_hole_spacing = 40.0
mount_hole_offset_y = 20.0
rib_thickness = 3.0
rib_height = 2.0
chamfer_size = 0.5

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

slot = Pos(0, slot_offset_y, 0) * Box(slot_width, slot_height, plate_thickness)
solid_body = solid_body - slot

boss = Pos(0, plate_height/2, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

cbore = Pos(0, plate_height/2, plate_thickness/2 + boss_height - counterbore_cbore_depth/2) * Cylinder(counterbore_cbore_diameter/2, counterbore_cbore_depth)
shaft = Pos(0, plate_height/2, plate_thickness/2 + boss_height/2) * Cylinder(counterbore_diameter/2, boss_height + plate_thickness + 10)
solid_body = solid_body - cbore - shaft

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, -plate_height/2 + mount_hole_offset_y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)
    solid_body = solid_body - hole

rib = Pos(-plate_width/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, plate_height, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")