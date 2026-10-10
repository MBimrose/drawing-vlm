from build123d import *

plate_width = 80.0
plate_length = 100.0
plate_thickness = 5.0
slot_width = 30.0
slot_length = 40.0
boss_radius = 12.0
boss_height = 12.0
counterbore_diameter = 8.0
counterbore_depth = 2.5
mount_hole_diameter = 6.0
mount_hole_spacing = 40.0
rib_thickness = 3.0
rib_height = 2.5
chamfer_size = 1.0

base = Box(plate_width, plate_length, plate_thickness)
slot = Pos(0, plate_length/2 - slot_length/2, 0) * Box(slot_width, slot_length, plate_thickness)
base = base - slot

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

boss = Pos(0, plate_length/2, plate_thickness/2 + boss_height/2) * Cylinder(boss_radius, boss_height)
base = base + boss

cbore = Pos(0, plate_length/2, plate_thickness/2 + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
base = base - cbore

through_hole = Pos(0, plate_length/2, plate_thickness/2 + boss_height/2) * Cylinder(counterbore_diameter/2, boss_height + plate_thickness + 10)
base = base - through_hole

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 10)
    base = base - hole

rib = Pos(-plate_width/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, plate_length, rib_height)
base = base + rib

part = base
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")