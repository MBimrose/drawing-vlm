from build123d import *

outer_size = 80.0
outer_height = 40.0
wall_thickness = 5.0
slot_width = 20.0
slot_height = 30.0
slot_offset_from_front = 10.0
lid_hole_diameter = 3.0
lid_hole_offset = 12.0
chamfer_distance = 0.5

outer_box = Box(outer_size, outer_size, outer_height)
inner_box = Box(outer_size - 2*wall_thickness, outer_size - 2*wall_thickness, outer_height - 2*wall_thickness)
shell = outer_box - inner_box

bottom_plate = Pos(0, 0, -(outer_height/2 - wall_thickness/2)) * Box(outer_size - 2*wall_thickness, outer_size - 2*wall_thickness, wall_thickness)
top_plate = Pos(0, 0, (outer_height/2 - wall_thickness/2)) * Box(outer_size - 2*wall_thickness, outer_size - 2*wall_thickness, wall_thickness)

case_body = shell + bottom_plate + top_plate

slot_cut = Pos(-(outer_size/2 - wall_thickness/2), slot_offset_from_front, 0) * Box(wall_thickness, slot_width, slot_height)
case_with_slot = case_body - slot_cut

hole_positions = [
    (outer_size/2 - lid_hole_offset, outer_size/2 - lid_hole_offset),
    (-outer_size/2 + lid_hole_offset, outer_size/2 - lid_hole_offset),
    (-outer_size/2 + lid_hole_offset, -outer_size/2 + lid_hole_offset),
    (outer_size/2 - lid_hole_offset, -outer_size/2 + lid_hole_offset),
]

case_with_holes = case_with_slot
for x, y in hole_positions:
    case_with_holes = case_with_holes - Pos(x, y, outer_height/2 - wall_thickness/2) * Cylinder(lid_hole_diameter/2, wall_thickness + 1)

vertical_edges = case_with_holes.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_distance)

part = result
part.name = "box_with_slot_and_holes"
export_step(part, "output.step")