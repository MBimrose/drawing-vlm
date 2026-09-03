from build123d import *

chute_length = 80.0
chute_width = 40.0
chute_height = 30.0
wall_thickness = 2.0
slot_width = 20.0
slot_depth = 20.0
hole_diameter = 6.0
hole_offset_x = 20.0
hole_offset_z = 15.0
chamfer_distance = 0.5

solid_body = Pos(0, 0, chute_height / 2) * Box(chute_length, chute_width, chute_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot = Pos(0, 0, slot_depth / 2) * Box(chute_length, slot_width, slot_depth)
solid_body = solid_body - slot

hole_x = hole_offset_x - chute_length / 2
hole_z = hole_offset_z
hole = Pos(hole_x, chute_width / 2, hole_z) * Rot(90, 0, 0) * Cylinder(hole_diameter / 2, chute_width * 2)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "chute"
export_step(part, "output.step")