from build123d import *

length = 80.0
flange_width = 40.0
flange_thickness = 5.0
web_height = 60.0
web_thickness = 4.0
hole_diameter = 6.0
chamfer_size = 0.5

flange = Pos(0, 0, length/2) * Box(flange_width, flange_thickness, length)
web = Pos(0, -(web_height/2 - flange_thickness/2), length/2) * Box(web_thickness, web_height, length)
result = flange + web

hole = Pos(0, 0, length/2) * Cylinder(hole_diameter/2, length)
result = result - hole

z_edges = result.edges().filter_by(Axis.Z)
result = chamfer(z_edges, chamfer_size)

part = result
part.name = "flange_web_with_hole"
export_step(part, "output.step")