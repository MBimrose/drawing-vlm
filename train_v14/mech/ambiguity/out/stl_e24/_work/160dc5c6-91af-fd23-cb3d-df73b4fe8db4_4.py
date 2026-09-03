from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
vent_slot_length = 50.0
vent_slot_height = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

vent_cut = Pos(0, -outer_width/2 + wall_thickness/2, outer_height/2) * Box(vent_slot_length, wall_thickness, vent_slot_height)
base = base - vent_cut

hole_r = mount_hole_diameter / 2
hole_h = outer_height + 10
for x, y in [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset)
]:
    base = base - Pos(x, y, outer_height/2) * Cylinder(hole_r, hole_h)

part = base
part.name = "vented_enclosure"
export_step(part, "output.step")