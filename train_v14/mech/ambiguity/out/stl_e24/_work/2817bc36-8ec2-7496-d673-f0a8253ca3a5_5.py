from build123d import *

beam_length = 80.0
beam_height = 60.0
flange_width = 40.0
web_thickness = 4.0
flange_thickness = 5.0
hole_diameter = 6.0
chamfer_size = 0.5

web = Box(web_thickness, beam_height, beam_length)
flange = Box(flange_width, flange_thickness, beam_length)
result = web + flange

result = result - Cylinder(hole_diameter/2, beam_length)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "I_beam_with_hole"
export_step(part, "output.step")