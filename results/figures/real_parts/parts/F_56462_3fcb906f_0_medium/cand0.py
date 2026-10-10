from build123d import *

outer_diameter = 30.0
wall_thickness = 0.8
inner_diameter = outer_diameter - 2 * wall_thickness
length = 30.0
flange_width = 80.0
flange_height = 40.0
flange_thickness = 5.0
slot_width = 10.0
slot_height = 20.0
slot_offset = 20.0
fillet_radius = 2.0
hole_diameter = inner_diameter - 1.5

cyl = Cylinder(outer_diameter / 2, length)
flange = Pos(0, flange_height / 2 - flange_thickness / 2, 0) * Box(flange_width, flange_thickness, length)
solid_body = cyl + flange

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

hole = Cylinder(hole_diameter / 2, length + 2)
solid_body = solid_body - hole

slot1 = Pos(-slot_offset, flange_height / 2 - flange_thickness / 2, 0) * Box(slot_width, flange_thickness, slot_height)
slot2 = Pos(slot_offset, flange_height / 2 - flange_thickness / 2, 0) * Box(slot_width, flange_thickness, slot_height)
solid_body = solid_body - slot1 - slot2

part = solid_body
part.name = "cylinder_with_flange"
export_step(part, "output.step")