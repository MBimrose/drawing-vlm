from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
pocket_length = 60.0
pocket_width = 40.0
pocket_depth = 3.0
central_hole_diameter = 12.0
mount_hole_diameter = 6.0
mount_hole_spacing = 30.0
mount_hole_offset_y = 10.0
slot_length = 40.0
slot_width = 4.0
slot_offset_y = -20.0
boss_diameter = 15.0
boss_height = 5.0
chamfer_size = 1.0
fillet_radius = 0.5

solid = Box(plate_length, plate_width, plate_thickness)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

solid = solid - Cylinder(central_hole_diameter/2, plate_thickness)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid = solid - Pos(x, mount_hole_offset_y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

solid = solid - Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness)

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid = solid + boss

solid = fillet(solid.edges().filter_by(Axis.Z), fillet_radius)

part = solid
part.name = "plate_with_pocket_holes_slot_boss"
export_step(part, "output.step")