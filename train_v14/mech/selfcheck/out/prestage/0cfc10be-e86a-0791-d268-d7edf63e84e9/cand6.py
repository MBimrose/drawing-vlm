from build123d import *

knob_diameter = 60.0
knob_height = 20.0
wall_thickness = 2.0
tab_width = 8.0
tab_height = 25.0
tab_length = 40.0
shaft_diameter = 6.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
chamfer_size = 1.0

solid_body = Cylinder(knob_diameter / 2, knob_height)
solid_body = solid_body - Cylinder(shaft_diameter / 2, knob_height)
solid_body = solid_body - Pos(0, 0, knob_height / 2 - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

tab = Pos(wall_thickness + tab_width / 2, tab_height / 2, knob_height / 2 + tab_length / 2) * Box(tab_width, tab_height, tab_length)
solid_body = solid_body + tab

part = solid_body
part.name = "knob_with_tab"
export_step(part, "output.step")