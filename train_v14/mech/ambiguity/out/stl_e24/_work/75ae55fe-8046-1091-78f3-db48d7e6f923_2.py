from build123d import *

length = 80.0
width = 25.0
thickness = 8.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 12.0
fillet_radius = 2.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
rib_height = 6.0
rib_width = 4.0
rib_spacing = 10.0

base = Pos(0, 0, width/2) * Box(length, thickness, width)

pocket = Pos(0, 0, width/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

base = fillet(base.edges().filter_by(Axis.Z), fillet_radius)

hole_r = mount_hole_diameter / 2
hole_tool = Rot(90, 0, 0) * Cylinder(hole_r, thickness + 2)
for x in [-length/2 + mount_hole_offset, length/2 - mount_hole_offset]:
    for z in [width/2 - mount_hole_offset, width/2 + mount_hole_offset]:
        base = base - Pos(x, 0, z) * hole_tool

rib_count = int((length - 2 * mount_hole_offset) // rib_spacing) + 1
rib_tool = Box(rib_width, rib_height, rib_width)
for i in range(rib_count):
    x = -length/2 + mount_hole_offset + i * rib_spacing
    base = base + Pos(x, thickness/2 + rib_height/2, width/2 + rib_width/2) * rib_tool

part = base
part.name = "plate_with_pocket_ribs"
export_step(part, "output.step")