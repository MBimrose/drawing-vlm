from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 1.5
vent_slot_length = 60.0
vent_slot_width = 4.0
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
chamfer_distance = 0.5

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length - 2*wall_thickness, outer_width - 2*wall_thickness, lid_thickness)
vent_slot = Pos(0, 0, outer_height + lid_thickness/2) * Box(vent_slot_length, vent_slot_width, lid_thickness)
lid = lid - vent_slot

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset),
]
for x, y in hole_positions:
    lid = lid - Pos(x, y, outer_height + lid_thickness/2) * Cylinder(mount_hole_diameter/2, lid_thickness)

result = base + lid
bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "vented_box_with_lid"
export_step(part, "output.step")