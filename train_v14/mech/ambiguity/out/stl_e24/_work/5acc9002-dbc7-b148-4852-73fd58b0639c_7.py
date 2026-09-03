from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 5.0
snap_tab_width = 4.0
snap_tab_height = 1.5
chamfer_size = 0.5
mount_hole_diameter = 3.0
mount_hole_offset = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 2.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

hole_r = mount_hole_diameter / 2
hole_h = outer_height + 10
for x in [outer_length/2, -outer_length/2]:
    for y in [mount_hole_offset, outer_width - mount_hole_offset]:
        for z in [mount_hole_offset, outer_height - mount_hole_offset]:
            base = base - Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
for y in [outer_width/2, -outer_width/2]:
    for x in [mount_hole_offset, outer_length - mount_hole_offset]:
        for z in [mount_hole_offset, outer_height - mount_hole_offset]:
            base = base - Pos(x, y, z) * Rot(90, 0, 0) * Cylinder(hole_r, hole_h)

base = base - Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length, outer_width, lid_thickness)
tab = Box(snap_tab_width, snap_tab_height, lid_thickness)
for x in [outer_length/2 - snap_tab_width/2, -(outer_length/2 - snap_tab_width/2)]:
    for y in [outer_width/2 - snap_tab_height/2, -(outer_width/2 - snap_tab_height/2)]:
        lid = lid + Pos(x, y, outer_height + lid_thickness/2) * tab

result = base + lid
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "snap_lid_box"
export_step(part, "output.step")