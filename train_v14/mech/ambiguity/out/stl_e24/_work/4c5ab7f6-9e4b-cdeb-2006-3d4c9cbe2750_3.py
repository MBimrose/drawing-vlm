from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 30.0
wall_thickness = 3.0
pocket_width = 30.0
pocket_depth = 20.0
pocket_height = 10.0
slot_width = 8.0
slot_height = 20.0
slot_offset = 5.0
hole_diameter = 4.0
hole_spacing = 20.0
chamfer_size = 0.5

base = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

pocket = Pos(0, 0, outer_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
base = base - pocket

slot_z = outer_height/2 + slot_offset
slot_y = Pos(0, outer_depth/2, slot_z) * Box(slot_width, outer_depth + 10, slot_height)
base = base - slot_y
slot_y_neg = Pos(0, -outer_depth/2, slot_z) * Box(slot_width, outer_depth + 10, slot_height)
base = base - slot_y_neg
slot_x = Pos(outer_width/2, 0, slot_z) * Box(outer_width + 10, slot_width, slot_height)
base = base - slot_x
slot_x_neg = Pos(-outer_width/2, 0, slot_z) * Box(outer_width + 10, slot_width, slot_height)
base = base - slot_x_neg

for dx, dy in [(-hole_spacing/2, -hole_spacing/2), (hole_spacing/2, -hole_spacing/2),
               (-hole_spacing/2, hole_spacing/2), (hole_spacing/2, hole_spacing/2)]:
    hole = Pos(dx, dy, outer_height/2) * Cylinder(hole_diameter/2, outer_height + 10)
    base = base - hole

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

part = base
part.name = "shelled_box_with_pockets_slots_holes"
export_step(part, "output.step")