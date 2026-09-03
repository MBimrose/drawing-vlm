from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 30.0
wall_thickness = 3.0
slot_width = 8.0
slot_height = 20.0
hole_diameter = 5.0
chamfer_size = 0.5

solid_body = Box(outer_width, outer_depth, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

slot_box = Box(outer_width + 10, slot_width, slot_height)
solid_body = solid_body - Pos(0, outer_depth/2, 0) * slot_box
solid_body = solid_body - Pos(0, -outer_depth/2, 0) * slot_box

slot_box2 = Box(slot_width, outer_depth + 10, slot_height)
solid_body = solid_body - Pos(outer_width/2, 0, 0) * slot_box2
solid_body = solid_body - Pos(-outer_width/2, 0, 0) * slot_box2

hole_cyl = Cylinder(hole_diameter/2, outer_height + 10)
solid_body = solid_body - Pos(0, 0, outer_height/2) * hole_cyl

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "shelled_box_with_slots_and_hole"
export_step(part, "output.step")