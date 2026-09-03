from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
rib_thickness = 2.0
rib_height = outer_height - 2 * wall_thickness - 5.0
rib_spacing = (outer_length - 2 * wall_thickness - 3 * rib_thickness) / 4.0
slot_width = 5.0
slot_height = 15.0
mount_hole_diameter = 3.0
mount_hole_offset = 10.0

base = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = offset(base, amount=-wall_thickness, openings=[top_face])

rib_positions = [
    -outer_length / 2 + wall_thickness + rib_spacing + rib_thickness / 2,
    0,
    outer_length / 2 - wall_thickness - rib_spacing - rib_thickness / 2,
]
for x in rib_positions:
    rib = Pos(x, 0, wall_thickness + rib_height / 2) * Box(rib_thickness, outer_width - 2 * wall_thickness, rib_height)
    base = base + rib

slot = Pos(0, -outer_width / 2 + wall_thickness / 2, outer_height / 2 - slot_height / 2) * Box(slot_width, wall_thickness, slot_height)
base = base - slot

hole_positions = [
    (-outer_length / 2 + mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (-outer_length / 2 + mount_hole_offset, outer_width / 2 - mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, outer_width / 2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, outer_height / 2) * Cylinder(mount_hole_diameter / 2, outer_height)
    base = base - hole

part = base
part.name = "hollow_box_with_ribs"
export_step(part, "output.step")