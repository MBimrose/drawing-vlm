from build123d import *

cyl_diameter = 30.0
cyl_length = 30.0
flange_width = 80.0
flange_height = 20.0
flange_thickness = 5.0
slot_width = 10.0
slot_height = 15.0
slot_depth = 4.0
hole_diameter = 18.5
chamfer_size = 1.0
fillet_radius = 2.0

cyl = Cylinder(cyl_diameter / 2, cyl_length)
flange = Pos(0, cyl_diameter / 2 + flange_thickness / 2, 0) * Box(flange_width, flange_thickness, cyl_length)
solid_body = cyl + flange

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

slot_cut = Pos(flange_width / 2 - slot_depth / 2, cyl_diameter / 2 + flange_thickness / 2, 0) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot_cut

hole_cut = Cylinder(hole_diameter / 2, cyl_length + flange_thickness + 10)
solid_body = solid_body - hole_cut

part = solid_body
part.name = "cylinder_with_flange"
export_step(part, "output.step")