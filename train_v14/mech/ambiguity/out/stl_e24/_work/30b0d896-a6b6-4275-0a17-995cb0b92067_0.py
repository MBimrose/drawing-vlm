from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
edge_chamfer = 1.0
pocket_width = 60.0
pocket_depth = 40.0
pocket_depth_cut = 4.0
central_hole_diameter = 12.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset_y = 10.0
slot_width = 40.0
slot_depth = 4.0
slot_offset_y = -20.0
boss_diameter = 15.0
boss_height = 5.0
fillet_radius = 0.5

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

solid_body = solid_body - Pos(0, 0, plate_thickness/2 - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(x, mount_hole_offset_y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

solid_body = solid_body - Pos(0, slot_offset_y, 0) * Box(slot_width, slot_depth, plate_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

part = solid_body
part.name = "plate_with_pocket_holes_and_boss"
export_step(part, "output.step")