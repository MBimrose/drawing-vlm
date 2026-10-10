from build123d import *

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
notch_width = 20.0
notch_depth = 40.0
boss_radius = 12.0
boss_height = 12.0
through_hole_diameter = 8.0
counterbore_diameter = 14.0
counterbore_depth = 2.5
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
mount_hole_offset = 20.0
rib_thickness = 3.0
rib_height = 3.0
chamfer_size = 0.5

result = Box(plate_width, plate_length, plate_thickness)

notch = Pos(plate_width/2 - notch_width/2, 0, 0) * Box(notch_width, notch_depth, plate_thickness)
result = result - notch

boss = Pos(0, plate_length/2, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
result = result + boss

through_hole = Pos(0, plate_length/2, 0) * Cylinder(through_hole_diameter/2, plate_thickness + boss_height + 10)
result = result - through_hole

cbore = Pos(0, plate_length/2, plate_thickness/2 + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
result = result - cbore

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, -plate_length/2 + mount_hole_offset, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)
    result = result - hole

rib = Pos(-plate_width/2 + rib_thickness/2, 0, plate_thickness/2 + rib_height/2) * Box(rib_thickness, plate_length, rib_height)
result = result + rib

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")