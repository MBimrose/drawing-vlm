from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 20.0
wall_thickness = 3.0
corner_radius = 5.0
vent_slot_width = 30.0
vent_slot_height = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 8.0

base = Box(outer_length, outer_width, outer_height)
base = fillet(base.edges().filter_by(Axis.Z), corner_radius)

inner = Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, outer_height)
result = base - inner

vent = Pos(outer_length/2 - wall_thickness/2, 0, 0) * Box(wall_thickness, vent_slot_width, vent_slot_height)
result = result - vent

hole_r = mount_hole_diameter / 2
hole_h = outer_height + 10
for x, y in [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset)
]:
    result = result - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

part = result
part.name = "hollow_box_with_vents_and_mounts"
export_step(part, "output.step")