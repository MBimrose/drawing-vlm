from build123d import *

shank_diameter = 10.0
shank_length = 55.0
head_diameter = 30.0
head_height = 10.0
thread_hole_diameter = 8.0
thread_hole_depth = 15.0
slot_width = 4.0
slot_height = 6.0
slot_depth = 2.0
slot_offset_from_bottom = 20.0
chamfer_size = 1.0

shank = Pos(0, 0, shank_length / 2) * Cylinder(shank_diameter / 2, shank_length)
head = Pos(0, 0, shank_length + head_height / 2) * Cylinder(head_diameter / 2, head_height)
body = shank + head

hole = Pos(0, 0, shank_length + head_height - thread_hole_depth / 2) * Cylinder(thread_hole_diameter / 2, thread_hole_depth)
body = body - hole

slot = Pos(shank_diameter / 2 - slot_depth / 2, 0, slot_offset_from_bottom + slot_height / 2) * Box(slot_depth, slot_width, slot_height)
body = body - slot

top_edges = body.edges().sort_by(Axis.Z)[-1:]
body = chamfer(top_edges, chamfer_size)

part = body
part.name = "bolt_with_slot"
export_step(part, "output.step")