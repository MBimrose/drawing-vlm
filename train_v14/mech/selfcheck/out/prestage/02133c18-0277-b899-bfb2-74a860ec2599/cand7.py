from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
rib_width = 5.0
rib_height = 2.0
central_hole_dia = 10.0
mount_hole_dia = 6.0
mount_hole_offset = 10.0
boss_dia = 15.0
boss_height = 2.0
pocket_depth = 2.0
pocket_margin = 10.0
chamfer_size = 0.5

base_plate = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
rib_outer = Pos(0, 0, rib_height/2) * Box(plate_length + 2*rib_width, plate_width + 2*rib_width, rib_height)
rib_inner = Pos(0, 0, rib_height/2) * Box(plate_length, plate_width, rib_height)
rib = rib_outer - rib_inner
boss = Pos(0, 0, boss_height/2) * Cylinder(boss_dia/2, boss_height)

result = base_plate + rib + boss

hole_height = plate_thickness + rib_height + boss_height + 10
result = result - Cylinder(central_hole_dia/2, hole_height)

mount_points = [
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
]
for x, y in mount_points:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, hole_height)

pocket = Pos(0, 0, plate_thickness + rib_height - pocket_depth/2) * Box(plate_length - 2*pocket_margin, plate_width - 2*pocket_margin, pocket_depth)
result = result - pocket

result = chamfer(result.edges(), chamfer_size)

part = result
part.name = "plate_with_rib_and_boss"
export_step(part, "output.step")