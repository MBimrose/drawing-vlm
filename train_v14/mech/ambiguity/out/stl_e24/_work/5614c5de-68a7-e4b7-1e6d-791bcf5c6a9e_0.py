from build123d import *

length = 80.0
width = 50.0
height = 20.0
wall_thickness = 3.0
corner_fillet = 5.0
slot_width = 10.0
slot_height = 12.0
central_hole_dia = 5.0

solid_body = Box(length, width, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, corner_fillet)

slot_box = Box(slot_width, slot_height, height)
solid_body = solid_body - Pos(-length/2 + wall_thickness/2, 0, 0) * slot_box
solid_body = solid_body - Pos(length/2 - wall_thickness/2, 0, 0) * slot_box

solid_body = solid_body - Cylinder(central_hole_dia/2, height)

part = solid_body
part.name = "shelled_box_with_slots_and_hole"
export_step(part, "output.step")