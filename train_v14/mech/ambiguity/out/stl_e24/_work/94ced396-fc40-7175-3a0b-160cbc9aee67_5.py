from build123d import *

plate_width = 80.0
plate_length = 100.0
plate_thickness = 4.0
cutout_width = 40.0
cutout_height = 60.0
boss_radius = 12.0
boss_height = 12.0
boss_hole_diameter = 8.0
counterbore_diameter = 14.0
counterbore_depth = 2.5
mount_hole_diameter = 6.0
mount_hole_spacing = 60.0
rib_thickness = 3.0
rib_height = 6.0
chamfer_size = 1.0

base = Box(plate_width, plate_length, plate_thickness)

cutout = Pos(0, plate_length/2 - cutout_height/2, 0) * Box(cutout_width, cutout_height, plate_thickness)
base = base - cutout

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    base = base - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib = Pos(-plate_width/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, plate_length, rib_height)
base = base + rib

boss = Pos(0, plate_length/2, boss_height/2) * Cylinder(boss_radius, boss_height)
base = base + boss

cbore = Pos(0, plate_length/2, boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
shaft = Pos(0, plate_length/2, boss_height/2) * Cylinder(boss_hole_diameter/2, boss_height + plate_thickness)
base = base - cbore - shaft

chamfer_edges = base.edges().filter_by(Axis.Z).sort_by(Axis.X)[:2]
base = chamfer(chamfer_edges, chamfer_size)

part = base
part.name = "plate_with_boss_and_rib"
export_step(part, "output.step")