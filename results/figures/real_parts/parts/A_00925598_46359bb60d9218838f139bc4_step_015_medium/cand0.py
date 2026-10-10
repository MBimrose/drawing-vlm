from build123d import *

plate_width = 80.0
plate_height = 80.0
plate_thickness = 15.0
boss_diameter = 50.0
boss_height = 60.0
central_hole_diameter = 30.0
mount_hole_diameter = 10.0
mount_hole_offset = 12.0
chamfer_distance = 5.0
fillet_radius = 2.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 10.0

solid_body = Box(plate_width, plate_height, plate_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness + boss_height + 20)

mount_points = [
    (plate_width/2 - mount_hole_offset, plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_height/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, -plate_height/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_height/2 + mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)
solid_body = chamfer(solid_body.faces().sort_by(Axis.Z)[0].edges(), chamfer_distance/2)
solid_body = fillet(solid_body.faces().sort_by(Axis.Z)[-1].edges(), fillet_radius)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height - pocket_depth/2) * Box(pocket_width, pocket_height, pocket_depth)

part = solid_body
part.name = "plate_with_boss_and_pocket"
export_step(part, "output.step")