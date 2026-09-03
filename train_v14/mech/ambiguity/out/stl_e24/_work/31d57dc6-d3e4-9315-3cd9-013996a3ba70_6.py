from build123d import *

pipe_outer_diameter = 40.0
pipe_wall_thickness = 3.0
pipe_length = 100.0
flange_length = 30.0
slot_width = 8.0
slot_length = 30.0
slot_depth = 1.5
chamfer_size = 0.5

outer_radius = pipe_outer_diameter / 2.0
inner_radius = outer_radius - pipe_wall_thickness

outer_cyl = Cylinder(outer_radius, pipe_length + flange_length)
inner_cyl = Cylinder(inner_radius, pipe_length + flange_length)
pipe_body = outer_cyl - inner_cyl

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_width, slot_depth, slot_length)
slot_box = chamfer(slot_box.edges(), chamfer_size)

result = pipe_body - slot_box

part = result
part.name = "pipe_with_slot"
export_step(part, "output.step")