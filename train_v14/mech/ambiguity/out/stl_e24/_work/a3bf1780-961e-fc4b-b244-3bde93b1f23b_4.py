from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
base_thickness = 8.0
pocket_length = 60.0
pocket_width = 40.0
pocket_depth = 10.0
mount_hole_diameter = 2.0
mount_hole_offset = 5.0
slot_width = 1.0
slot_height = 10.0
slot_depth = wall_thickness + 0.5

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness

solid_body = Pos(0, 0, outer_height / 2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

base_plate = Pos(0, 0, base_thickness / 2) * Box(inner_length, inner_width, base_thickness)
solid_body = solid_body + base_plate

pocket = Pos(0, 0, outer_height - pocket_depth / 2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole_positions = [
    (-outer_length / 2 + mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, -outer_width / 2 + mount_hole_offset),
    (-outer_length / 2 + mount_hole_offset, outer_width / 2 - mount_hole_offset),
    (outer_length / 2 - mount_hole_offset, outer_width / 2 - mount_hole_offset),
]
for x, y in hole_positions:
    hole = Pos(x, y, outer_height / 2) * Cylinder(mount_hole_diameter / 2, outer_height)
    solid_body = solid_body - hole

left_slot = Pos(-outer_length / 2 + wall_thickness + slot_depth / 2, 0, outer_height / 2) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - left_slot

right_slot = Pos(outer_length / 2 - wall_thickness - slot_depth / 2, 0, outer_height / 2) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - right_slot

part = solid_body
part.name = "hollow_box_with_pocket_and_slots"
export_step(part, "output.step")