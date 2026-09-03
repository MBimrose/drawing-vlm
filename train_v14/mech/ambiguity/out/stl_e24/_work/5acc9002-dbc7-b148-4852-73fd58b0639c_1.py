from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
lid_thickness = 5.0
snap_slot_width = 1.5
snap_slot_depth = lid_thickness
chamfer_size = 0.5
mount_hole_dia = 3.0
mount_hole_spacing = 40.0

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[bottom_face])

lid = Pos(0, 0, outer_height + lid_thickness/2) * Box(outer_length, outer_width, lid_thickness)
result = base + lid

slot_positions = [
    (outer_length/2 - snap_slot_width/2, outer_width/2 - snap_slot_width/2),
    (-outer_length/2 + snap_slot_width/2, outer_width/2 - snap_slot_width/2),
    (outer_length/2 - snap_slot_width/2, -outer_width/2 + snap_slot_width/2),
    (-outer_length/2 + snap_slot_width/2, -outer_width/2 + snap_slot_width/2),
]
for x, y in slot_positions:
    slot = Pos(x, y, outer_height + lid_thickness - snap_slot_depth/2) * Box(snap_slot_width, snap_slot_depth, snap_slot_depth)
    result = result - slot

hole_z = outer_height/2 - mount_hole_spacing/2
for x in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    result = result - Pos(x, outer_width/2, hole_z) * Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, outer_width + 10)
    result = result - Pos(x, -outer_width/2, hole_z) * Rot(90, 0, 0) * Cylinder(mount_hole_dia/2, outer_width + 10)

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "enclosure_with_lid"
export_step(part, "output.step")