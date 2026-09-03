from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 30.0
wall_thickness = 3.0
slot_width = 8.0
slot_height = 20.0
central_hole_dia = 4.0
chamfer_size = 0.5

solid = Pos(0, 0, outer_height/2) * Box(outer_width, outer_depth, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = offset(solid, amount=-wall_thickness, openings=[top_face, bottom_face])

slot_box = Box(slot_width, slot_width, slot_height)
solid = solid - Pos(0, outer_depth/2 - slot_width/2, outer_height/2) * slot_box
solid = solid - Pos(0, -outer_depth/2 + slot_width/2, outer_height/2) * slot_box
solid = solid - Pos(outer_width/2 - slot_width/2, 0, outer_height/2) * slot_box
solid = solid - Pos(-outer_width/2 + slot_width/2, 0, outer_height/2) * slot_box

solid = solid - Cylinder(central_hole_dia/2, outer_height * 2)
solid = chamfer(solid.edges().filter_by(Axis.Z), chamfer_size)

part = solid
part.name = "hollow_box_with_slots"
export_step(part, "output.step")