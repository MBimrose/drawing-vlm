from build123d import *

shaft_length = 60.0
shaft_diameter = 10.0
shaft_radius = shaft_diameter / 2.0
tab_width = 12.0
tab_height = 8.0
tab_thickness = 4.0
hole_diameter = 6.0
hole_depth = 35.0
slot_width = 4.0
slot_depth = 2.0
chamfer_size = 0.5

shaft = Pos(shaft_length / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(shaft_radius, shaft_length)
tab = Pos(shaft_length, 0, 0) * Box(tab_thickness, tab_width, tab_height)
result = shaft + tab

hole = Pos(shaft_length - hole_depth / 2, 0, 0) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, hole_depth)
result = result - hole

slot = Pos(shaft_length + tab_thickness / 2, 0, 0) * Box(slot_depth, slot_width, tab_height)
result = result - slot

x_face = result.faces().sort_by(Axis.X)[-1]
result = chamfer(x_face.edges(), chamfer_size)

part = result
part.name = "shaft_with_tab"
export_step(part, "output.step")