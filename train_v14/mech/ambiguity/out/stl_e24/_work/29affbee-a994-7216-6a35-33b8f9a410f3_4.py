from build123d import *

rod_length = 80.0
rod_diameter = 20.0
rod_radius = rod_diameter / 2.0
hole_diameter = 8.0
hole_radius = hole_diameter / 2.0
slot_width = 6.0
slot_length = 12.0
slot_depth = rod_radius - 2.0
slot_center_z = rod_length * 0.75
chamfer_size = 1.0

solid_body = Cylinder(rod_radius, rod_length)
solid_body = solid_body - Cylinder(hole_radius, rod_length)
slot_box = Pos(0, slot_depth / 2, slot_center_z) * Box(slot_length, slot_depth, slot_width)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "rod_with_slot_and_chamfer"
export_step(part, "output.step")