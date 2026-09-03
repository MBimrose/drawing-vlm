from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 5.0
slot_length = 20.0
slot_width = 5.0
slot_depth = 3.0
hole_diameter = 4.0
hole_depth = 6.0
chamfer_size = 0.5

solid_body = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

pocket = Pos(0, 0, outer_height - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid_body = solid_body - pocket

slot = Pos(outer_length/2 - slot_depth/2, 0, outer_height/2) * Box(slot_depth, slot_length, slot_width)
solid_body = solid_body - slot

hole = Pos(outer_length/2 - hole_depth/2, 0, outer_height/2) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, hole_depth)
solid_body = solid_body - hole

part = solid_body
part.name = "hollow_box_with_pocket_slot_hole"
export_step(part, "output.step")