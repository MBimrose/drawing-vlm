from build123d import *

beam_length = 80.0
flange_width = 50.0
flange_thickness = 12.0
web_height = 30.0
web_thickness = 10.0
hole_diameter = 5.0
hole_spacing_x = 30.0
hole_spacing_y = 15.0
chamfer_size = 1.0
slot_width = 6.0
slot_length = 20.0

web = Box(web_thickness, web_height, beam_length)
flange = Pos(0, web_height/2 + flange_thickness/2, 0) * Box(flange_width, flange_thickness, beam_length)
solid_body = web + flange

hole_r = hole_diameter / 2
hole_h = beam_length + 10
for x in [-hole_spacing_x/2, hole_spacing_x/2]:
    for y in [-hole_spacing_y/2, hole_spacing_y/2]:
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

slot = Pos(0, web_height/2 + flange_thickness/2, beam_length/2 - flange_thickness/2) * Box(slot_length, slot_width, flange_thickness)
solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "T-beam"
export_step(part, "output.step")