from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_thickness = 8.0
pocket_length = 60.0
pocket_width = 40.0
pocket_depth = 10.0
pocket_chamfer = 1.0
mount_hole_dia = 2.0
mount_hole_offset = 5.0
rib_thickness = 1.5
rib_width = 10.0
rib_height = 12.0

base = Pos(0, 0, base_thickness/2) * Box(outer_length, outer_width, base_thickness)
outer_box = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
inner_box = Pos(0, 0, base_thickness + (outer_height - base_thickness)/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, outer_height - base_thickness)
walls = outer_box - inner_box
result = base + walls

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
pocket = chamfer(pocket.edges().filter_by(Axis.Z), pocket_chamfer)
result = result - pocket

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, outer_height/2) * Cylinder(mount_hole_dia/2, outer_height + 10)

rib_left = Pos(-outer_length/2 + wall_thickness + rib_width/2, 0, base_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
rib_right = Pos(outer_length/2 - wall_thickness - rib_width/2, 0, base_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
result = result + rib_left + rib_right

part = result
part.name = "box_with_pocket_and_ribs"
export_step(part, "output.step")