from build123d import *

beam_length = 80.0
beam_height = 30.0
flange_width = 50.0
flange_thickness = 12.0
web_thickness = 10.0
groove_width = 6.0
groove_depth = 4.0
groove_spacing = 12.0
groove_count = 4
hole_diameter = 4.0
hole_spacing_x = 15.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
chamfer_size = 1.0

web = Box(web_thickness, beam_height, beam_length)
flange = Pos(0, beam_height/2 + flange_thickness/2, 0) * Box(flange_width, flange_thickness, beam_length)
result = web + flange

for i in range(groove_count):
    x = (i - (groove_count - 1) / 2) * groove_spacing
    result = result - Pos(x, beam_height/2 + flange_thickness - groove_depth/2, 0) * Box(groove_width, groove_depth, beam_length)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, beam_length)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "T-beam_with_grooves_and_holes"
export_step(part, "output.step")