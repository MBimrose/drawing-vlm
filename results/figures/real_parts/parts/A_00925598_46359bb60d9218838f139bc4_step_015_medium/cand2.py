from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 15.0
corner_chamfer = 5.0
mount_hole_dia = 8.0
mount_hole_offset = 10.0
boss_outer_dia = 50.0
boss_inner_dia = 30.0
boss_height = 60.0
pocket_width = 30.0
pocket_length = 20.0
pocket_depth = 10.0
edge_chamfer = 1.0
clearance = 0.2

plate = Box(plate_width, plate_length, plate_thickness)
plate = chamfer(plate.edges().filter_by(Axis.Z), corner_chamfer)

hole_positions = [
    (plate_width/2 - mount_hole_offset, plate_length/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, plate_length/2 - mount_hole_offset),
    (-plate_width/2 + mount_hole_offset, -plate_length/2 + mount_hole_offset),
    (plate_width/2 - mount_hole_offset, -plate_length/2 + mount_hole_offset),
]
for x, y in hole_positions:
    plate = plate - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

boss = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_outer_dia/2, boss_height)
result = plate + boss

bore = Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_inner_dia/2, boss_height + plate_thickness)
result = result - bore

pocket = Pos(0, 0, plate_thickness/2 + boss_height - pocket_depth/2) * Box(pocket_width, pocket_length, pocket_depth)
result = result - pocket

result = chamfer(result.edges(), edge_chamfer)

part = result
part.name = "plate_with_boss"
export_step(part, "output.step")