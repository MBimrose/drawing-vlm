from build123d import *

outer_width = 50.0
outer_depth = 60.0
outer_height = 30.0
wall_thickness = 5.0
split_gap = 2.0
split_depth = 15.0
chamfer_size = 1.0
mount_hole_diameter = 4.0
mount_hole_spacing = 40.0

base = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
inner = Pos(0, 0, outer_height/2) * Box(outer_width - 2*wall_thickness, outer_depth - 2*wall_thickness, outer_height)
result = base - inner

split_cut = Pos(0, -outer_depth/2 + split_depth/2, 0) * Box(split_gap, split_depth, outer_height)
result = result - split_cut

bottom_front_edges = result.edges().filter_by(Axis.X).sort_by(Axis.Z)[:1]
result = chamfer(bottom_front_edges, chamfer_size)

for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, 0, outer_height/2) * Cylinder(mount_hole_diameter/2, outer_height)

part = result
part.name = "XMountSocket"
export_step(part, "output.step")