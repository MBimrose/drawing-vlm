from build123d import *

beam_length = 80.0
flange_width = 50.0
flange_thickness = 12.0
web_height = 30.0
web_thickness = 10.0
groove_width = 4.0
groove_depth = 2.0
hole_diameter = 4.0
hole_offset_x = beam_length / 4.0
chamfer_size = 1.0

web = Box(web_thickness, web_height, beam_length)
flange = Pos(0, web_height / 2.0 + flange_thickness / 2.0, 0) * Box(flange_width, flange_thickness, beam_length)
result = web + flange

groove = Pos(0, web_height / 2.0 + flange_thickness - groove_depth / 2.0, 0) * Box(groove_width, groove_depth, beam_length)
result = result - groove

for x in [hole_offset_x, beam_length - hole_offset_x]:
    hole = Pos(x, web_height / 2.0 + flange_thickness / 2.0, 0) * Cylinder(hole_diameter / 2.0, beam_length)
    result = result - hole

vertical_edges = result.edges().filter_by(Axis.Z)
flange_edges = [e for e in vertical_edges if e.center().Y > 0]
result = chamfer(flange_edges, chamfer_size)

part = result
part.name = "T_beam_with_groove_and_holes"
export_step(part, "output.step")