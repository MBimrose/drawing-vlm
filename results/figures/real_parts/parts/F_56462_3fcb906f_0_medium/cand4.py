from build123d import *

cyl_diameter = 30.0
cyl_length = 40.0
flange_width = 80.0
flange_thickness = 5.0
flange_height = 20.0
wall_thickness = 0.6
chamfer_size = 0.5
hole_diameter = 18.5

cyl = Cylinder(cyl_diameter / 2, cyl_length)
flange = Pos(0, cyl_diameter / 2 + flange_thickness / 2, 0) * Box(flange_width, flange_thickness, cyl_length)
solid_body = cyl + flange
solid_body = offset(solid_body, amount=-wall_thickness)
solid_body = solid_body - Cylinder(hole_diameter / 2, cyl_length + 20)
z_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(z_edges, chamfer_size)

part = solid_body
part.name = "cylinder_with_flange"
export_step(part, "output.step")