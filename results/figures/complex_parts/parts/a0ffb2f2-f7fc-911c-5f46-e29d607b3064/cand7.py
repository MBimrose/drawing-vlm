from build123d import *

head_diameter = 30.0
head_height = 10.0
shank_diameter = 10.0
shank_length = 50.0
central_hole_diameter = 5.0
counterbore_diameter = 8.0
counterbore_depth = 5.0
slot_width = 4.0
slot_length = 10.0
chamfer_size = 0.5

shank = Pos(0, 0, shank_length / 2) * Cylinder(shank_diameter / 2, shank_length)
head = Pos(0, 0, shank_length + head_height / 2) * Cylinder(head_diameter / 2, head_height)
solid_body = shank + head

total_height = shank_length + head_height
solid_body = solid_body - Pos(0, 0, total_height / 2) * Cylinder(central_hole_diameter / 2, total_height)
solid_body = solid_body - Pos(0, 0, total_height - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

slot = Pos(0, 0, shank_length + head_height / 2) * Box(head_diameter, slot_width, slot_length)
solid_body = solid_body - slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "pin_with_slot"
export_step(part, "output.step")