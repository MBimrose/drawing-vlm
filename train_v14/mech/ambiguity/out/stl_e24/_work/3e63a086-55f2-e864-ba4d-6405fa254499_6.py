from build123d import *

block_length = 70.0
block_width = 40.0
block_height = 20.0
rib_length = 50.0
rib_width = 12.0
rib_height = 8.0
central_hole_diameter = 10.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
chamfer_distance = 1.5
fillet_radius = 2.0

base = Pos(0, 0, block_height/2) * Box(block_length, block_width, block_height)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, block_height + rib_height/2) * Box(rib_length, rib_width, rib_height)
rib = fillet(rib.edges().filter_by(Axis.Z), fillet_radius)

combined = base + rib

hole_height = block_height + rib_height + 10
central_hole = Pos(0, 0, (block_height + rib_height)/2) * Cylinder(central_hole_diameter/2, hole_height)
combined = combined - central_hole

mount_hole = Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, block_width + 10)
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    combined = combined - Pos(x, 0, block_height + rib_height/2) * mount_hole

part = combined
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")