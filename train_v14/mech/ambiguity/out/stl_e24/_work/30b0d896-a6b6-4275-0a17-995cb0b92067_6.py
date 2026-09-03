from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
edge_chamfer = 1.0
top_fillet = 0.5
central_hole_dia = 12.0
mount_hole_dia = 6.0
mount_hole_spacing = 30.0
mount_hole_offset = 10.0
pocket_width = 60.0
pocket_depth = 40.0
pocket_depth_cut = 4.0
slot_width = 4.0
slot_length = 40.0
boss_dia = 15.0
boss_height = 5.0

solid = Box(plate_width, plate_depth, plate_thickness)
solid = chamfer(solid.edges().filter_by(Axis.Z), edge_chamfer)
solid = solid - Cylinder(central_hole_dia/2, plate_thickness)
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid = solid - Pos(x, mount_hole_offset, 0) * Cylinder(mount_hole_dia/2, plate_thickness)
solid = solid - Pos(0, 0, plate_thickness/2 - pocket_depth_cut/2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid = solid - Pos(0, -plate_depth/2 + slot_width/2 + 5, 0) * Box(slot_length, slot_width, plate_thickness)
solid = solid + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_dia/2, boss_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
solid = fillet(top_face.edges(), top_fillet)

part = solid
part.name = "plate_with_features"
export_step(part, "output.step")