from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 4.0
slot_width = 20.0
slot_height = 30.0
slot_offset_x = 20.0
slot_offset_y = 0.0
fillet_radius = 3.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_edge_margin = 5.0
rib_height = 2.0
rib_width = 6.0
rib_length = bracket_width - 10.0

result = Box(bracket_length, bracket_width, bracket_thickness)

slot_body = Pos(slot_offset_x, slot_offset_y, 0) * Box(slot_width, slot_height, bracket_thickness)
slot_body = fillet(slot_body.edges().filter_by(Axis.Z), fillet_radius)
result = result - slot_body

hole_x = -bracket_length / 2 + hole_edge_margin + hole_diameter / 2
for y in [-hole_spacing / 2, hole_spacing / 2]:
    result = result - Pos(hole_x, y, 0) * Cylinder(hole_diameter / 2, bracket_thickness)

rib = Pos(bracket_length / 2 + rib_width / 2, 0, 0) * Box(rib_width, rib_length, rib_height)
result = result + rib

part = result
part.name = "bracket_with_slot_rib_holes"
export_step(part, "output.step")