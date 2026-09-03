from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 5.0
snap_tab_width = 4.0
snap_tab_height = 3.0
snap_tab_spacing = 6.0
mount_hole_diameter = 3.0
mount_hole_offset = 5.0
chamfer_size = 0.5

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
inner = Pos(0, 0, (outer_height - lid_thickness)/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, outer_height - lid_thickness)
base = base - inner

hole_r = mount_hole_diameter / 2
hole_len = outer_length + 20
for x in [-(outer_length/2 - mount_hole_offset), outer_length/2 - mount_hole_offset]:
    for y in [-(outer_width/2 - mount_hole_offset), outer_width/2 - mount_hole_offset]:
        base = base - Pos(x, y, mount_hole_offset) * Rot(90, 0, 0) * Cylinder(hole_r, hole_len)

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length, outer_width, lid_thickness)
for x in [-(outer_length/2 - snap_tab_spacing), outer_length/2 - snap_tab_spacing]:
    for y in [-(outer_width/2 - snap_tab_spacing), outer_width/2 - snap_tab_spacing]:
        lid = lid - Pos(x, y, outer_height + lid_thickness/2) * Box(snap_tab_width, snap_tab_height, lid_thickness)

lid = chamfer(lid.edges().filter_by(Axis.Z), chamfer_size)

part = base + lid
part.name = "box_with_lid"
export_step(part, "output.step")