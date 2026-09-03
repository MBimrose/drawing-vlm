from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 4.0
slot_width = 20.0
slot_length = 30.0
slot_offset_from_right = 5.0
fillet_radius = 3.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_from_left = 8.0
rib_width = 6.0
rib_height = 2.0
rib_length = bracket_width - 10.0

base = Box(bracket_length, bracket_width, bracket_thickness)

slot_center_x = bracket_length / 2 - slot_offset_from_right - slot_width / 2
slot_cut = Pos(slot_center_x, 0, 0) * Box(slot_width, slot_length, bracket_thickness)
slot_cut = fillet(slot_cut.edges().filter_by(Axis.Z), fillet_radius)

result = base - slot_cut

hole_center_x = -bracket_length / 2 + hole_offset_from_left
for y in [-hole_spacing / 2, hole_spacing / 2]:
    result = result - Pos(hole_center_x, y, 0) * Cylinder(hole_diameter / 2, bracket_thickness)

rib = Pos(bracket_length / 2 + rib_width / 2, 0, 0) * Box(rib_width, rib_length, rib_height)
result = result + rib

part = result
part.name = "bracket"
export_step(part, "output.step")