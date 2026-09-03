from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 3.0
chamfer_size = 0.5
mount_hole_diameter = 2.0
mount_hole_offset = 5.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

bottom_face = base.faces().sort_by(Axis.Z)[0]
base = chamfer(bottom_face.edges(), chamfer_size)

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length, outer_width, lid_thickness)
result = base + lid

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, outer_height + lid_thickness/2) * Cylinder(mount_hole_diameter/2, 100)

part = result
part.name = "box_with_lid_and_mount_holes"
export_step(part, "output.step")