from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
edge_chamfer = 1.0
pocket_margin = 10.0
pocket_depth = 3.0
central_hole_diameter = 12.0
boss_diameter = 15.0
boss_height = 5.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset_y = 10.0
slot_width = 4.0
slot_length = 40.0
slot_offset_y = -20.0
fillet_radius = 0.5

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

pocket_w = plate_width - 2 * pocket_margin
pocket_d = plate_depth - 2 * pocket_margin
pocket_box = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_w, pocket_d, pocket_depth)
solid_body = solid_body - pocket_box

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness)

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, mount_hole_offset_y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

slot_box = Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot_box

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_pocket_and_boss"
export_step(part, "output.step")