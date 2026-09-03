from build123d import *

length = 80.0
height = 60.0
flange_width = 40.0
flange_thickness = 5.0
web_thickness = 4.0
hole_diameter = 6.0
chamfer_size = 0.5

flange = Box(flange_width, flange_thickness, length)
web = Box(web_thickness, height, length)
solid_body = flange + web

solid_body = solid_body - Cylinder(hole_diameter/2, length)

z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)

part = solid_body
part.name = "flange_web_with_hole"
export_step(part, "output.step")