from build123d import *

beam_length = 80.0
flange_width = 50.0
flange_thickness = 12.0
web_height = 30.0
web_thickness = 10.0
chamfer_size = 1.0

flange = Pos(0, web_height/2 + flange_thickness/2, 0) * Box(flange_width, flange_thickness, beam_length)
web = Pos(0, 0, 0) * Box(web_thickness, web_height, beam_length)
result = flange + web

vertical_edges = result.edges().filter_by(Axis.Z)
flange_edges = [e for e in vertical_edges if e.center().Y > 0]
result = chamfer(flange_edges, chamfer_size)

part = result
part.name = "T-beam"
export_step(part, "output.step")