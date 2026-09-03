from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 2.0
recess_margin = 5.0
recess_depth = 1.5
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
chamfer_size = 0.5

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length, outer_width, lid_thickness)
result = base + lid

recess_w = outer_length - 2 * recess_margin
recess_d = outer_width - 2 * recess_margin
recess = Pos(0, 0, outer_height + lid_thickness - recess_depth/2) * Box(recess_w, recess_d, recess_depth)
result = result - recess

hole_r = mount_hole_diameter / 2
hole_h = outer_height + lid_thickness + 10
hole_z = (outer_height + lid_thickness) / 2
for x in [-outer_length/2 + mount_hole_offset, outer_length/2 - mount_hole_offset]:
    for y in [-outer_width/2 + mount_hole_offset, outer_width/2 - mount_hole_offset]:
        result = result - Pos(x, y, hole_z) * Cylinder(hole_r, hole_h)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_size)

part = result
part.name = "box_with_lid"
export_step(part, "output.step")