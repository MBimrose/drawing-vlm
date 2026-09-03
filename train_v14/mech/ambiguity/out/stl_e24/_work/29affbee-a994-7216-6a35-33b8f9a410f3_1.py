from build123d import *

bar_length = 80.0
bar_diameter = 20.0
bar_radius = bar_diameter / 2.0
hole_diameter = 8.0
pocket_width = 12.0
pocket_depth = 10.0
pocket_offset = 20.0
chamfer_size = 1.0
slot_width = 6.0
slot_length = 30.0
slot_offset = 5.0

solid_body = Cylinder(bar_radius, bar_length)
solid_body = solid_body - Cylinder(hole_diameter / 2, bar_length)

pocket_box = Pos(0, bar_radius - pocket_depth / 2, pocket_offset) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket_box

slot_box = Pos(0, bar_radius - slot_width / 2, slot_offset) * Box(slot_length, slot_width, slot_width)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "bar_with_pocket_and_slot"
export_step(part, "output.step")