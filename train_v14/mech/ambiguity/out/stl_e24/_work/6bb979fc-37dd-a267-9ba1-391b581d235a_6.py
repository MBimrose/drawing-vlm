from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
snap_tab_width = 12.0
snap_tab_height = 6.0
snap_tab_thickness = 3.0
snap_tab_flex_depth = 1.0
snap_tab_flex_width = 4.0
snap_tab_flex_length = 10.0
rib_thickness = 2.0
rib_height = 5.0
mount_hole_diameter = 3.0
mount_hole_spacing = 20.0
mount_hole_offset = 10.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

tab = Pos(0, outer_width/2 + snap_tab_thickness/2, outer_height/2 - snap_tab_height/2 - 5) * Box(snap_tab_width, snap_tab_thickness, snap_tab_height)
base = base + tab

flex_cut = Pos(0, outer_width/2 + snap_tab_thickness - snap_tab_flex_depth/2, outer_height/2 - snap_tab_height/2 - 5) * Box(snap_tab_flex_length, snap_tab_flex_depth, snap_tab_flex_width)
base = base - flex_cut

rib = Pos(0, -outer_width/2 - rib_thickness/2, outer_height/2 - rib_height/2 - 5) * Box(rib_thickness, rib_thickness, rib_height)
base = base + rib

hole_r = mount_hole_diameter / 2
hole_h = outer_length + 20
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    for y in [-mount_hole_offset, mount_hole_offset]:
        base = base - Pos(x, y, outer_height/2) * Cylinder(hole_r, hole_h)

part = base
part.name = "snap_fit_box"
export_step(part, "output.step")