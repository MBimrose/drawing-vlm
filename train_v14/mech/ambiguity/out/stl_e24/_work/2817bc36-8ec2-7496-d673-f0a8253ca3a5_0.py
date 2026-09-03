from build123d import *

beam_length = 80.0
beam_height = 60.0
flange_width = 40.0
web_thickness = 4.0
flange_thickness = 5.0
chamfer_size = 0.5
hole_diameter = 6.0

web = Box(web_thickness, beam_height, beam_length)
top_flange = Pos(0, beam_height/2 - flange_thickness/2, 0) * Box(flange_width, flange_thickness, beam_length)
bottom_flange = Pos(0, -beam_height/2 + flange_thickness/2, 0) * Box(flange_width, flange_thickness, beam_length)

solid_body = web + top_flange + bottom_flange
solid_body = solid_body - Cylinder(hole_diameter/2, beam_length)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "I-beam"
export_step(part, "output.step")