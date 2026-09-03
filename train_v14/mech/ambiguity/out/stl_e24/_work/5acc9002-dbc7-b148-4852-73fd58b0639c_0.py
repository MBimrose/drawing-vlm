from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 5.0
snap_notch_width = 4.0
snap_notch_depth = 1.5
chamfer_size = 0.5
mount_hole_diameter = 3.0
mount_hole_offset = 5.0

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

hole_r = mount_hole_diameter / 2
hole_tool = Rot(90, 0, 0) * Cylinder(hole_r, outer_width + 10)
for x in [-inner_length/2 + mount_hole_offset, inner_length/2 - mount_hole_offset]:
    for z in [mount_hole_offset, outer_height - mount_hole_offset]:
        base = base - Pos(x, 0, z) * hole_tool

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length, outer_width, lid_thickness)
notch_tool = Box(snap_notch_width, snap_notch_depth, lid_thickness)
for x in [-outer_length/2 + snap_notch_width/2, outer_length/2 - snap_notch_width/2]:
    for y in [-outer_width/2 + snap_notch_depth/2, outer_width/2 - snap_notch_depth/2]:
        lid = lid - Pos(x, y, outer_height + lid_thickness/2) * notch_tool

result = base + lid
result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "snap_fit_enclosure"
export_step(part, "output.step")