from build123d import *

block_length = 70.0
block_width = 40.0
block_height = 20.0
rib_length = 50.0
rib_width = 12.0
rib_height = 8.0
hole_diameter = 10.0
fillet_radius = 3.0
chamfer_distance = 1.5
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0

base = Box(block_length, block_width, block_height)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_distance)

rib = Pos(0, 0, block_height/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
rib = fillet(rib.edges().filter_by(Axis.Z), fillet_radius)

result = base + rib

hole_cyl = Cylinder(hole_diameter/2, block_height + rib_height + 20)
result = result - hole_cyl

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    mount_hole = Pos(x, 0, block_height/2 + rib_height/2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, rib_width + 20)
    result = result - mount_hole

part = result
part.name = "block_with_rib_and_holes"
export_step(part, "output.step")