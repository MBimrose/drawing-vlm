from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
width = 20.0
tab_width = 20.0
tab_height = 12.0
groove_depth = 4.0
groove_width = 6.0
chamfer_size = 1.0
mount_hole_diameter = 8.0
mount_hole_spacing = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

ring = Cylinder(outer_radius, width) - Cylinder(inner_radius, width)

tab = Pos(0, outer_radius, 0) * Box(tab_width, tab_height, width)
tab = chamfer(tab.edges().filter_by(Axis.Z), chamfer_size)

result = ring + tab

groove = Pos(0, 0, width/2 - groove_depth/2) * Cylinder(inner_radius - groove_width/2, groove_depth)
result = result - groove

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Cylinder(mount_hole_diameter/2, width)

part = result
part.name = "ring_with_tab"
export_step(part, "output.step")