from build123d import *

plate_width = 80.0
plate_height = 100.0
plate_thickness = 5.0
slot_width = 30.0
slot_depth = 20.0
slot_offset_from_top = 10.0
boss_radius = 12.0
boss_height = 12.0
counterbore_diameter = 8.0
counterbore_depth = 4.0
mount_hole_diameter = 6.0
mount_hole_spacing = 50.0
mount_hole_offset_y = 20.0
chamfer_size = 0.5
rib_thickness = 3.0
rib_height = 4.0

solid_body = Box(plate_width, plate_height, plate_thickness)

slot_center_y = plate_height/2 - slot_offset_from_top - slot_depth/2
slot_cut = Pos(0, slot_center_y, 0) * Box(slot_width, slot_depth, plate_thickness)
solid_body = solid_body - slot_cut

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

boss_center_y = plate_height/2
boss = Pos(0, boss_center_y, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

cbore = Pos(0, boss_center_y, plate_thickness/2 + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

rib = Pos(-plate_width/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, plate_height, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_slot_boss_and_rib"
export_step(part, "output.step")