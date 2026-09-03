from build123d import *

plate_width = 80.0
plate_depth = 20.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 30.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_angle = 90.0
mount_hole_diameter = 4.0
mount_hole_offset = 20.0
notch_radius = 2.0
chamfer_size = 0.5
rib_width = 60.0
rib_depth = 3.0
rib_height = 2.0
rib_offset = 5.0

base = Box(plate_width, plate_depth, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

notch = Pos(plate_width/2, 0, 0) * Cylinder(notch_radius, plate_thickness + 1)
base = base - notch

for x in [-plate_width/2 + mount_hole_offset, plate_width/2 - mount_hole_offset]:
    base = base - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

rib = Pos(-plate_width/2 + rib_offset + rib_width/2, 0, -plate_thickness/2 + rib_height/2) * Box(rib_width, rib_depth, rib_height)
base = base + rib

boss = Cylinder(boss_diameter/2, boss_height)
boss = boss - Cylinder(set_screw_diameter/2, boss_height + 1)
boss = boss - Pos(0, 0, boss_height/2) * CounterSinkHole(set_screw_diameter/2, set_screw_head_diameter/2, boss_height, set_screw_head_angle)

part = base + boss
part.name = "plate_with_boss"
export_step(part, "output.step")