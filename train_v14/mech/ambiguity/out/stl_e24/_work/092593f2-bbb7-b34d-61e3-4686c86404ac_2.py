from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 4.0
slot_width = 20.0
slot_height = 24.0
slot_offset_from_right = 10.0
fillet_radius = 3.0
hole_diameter = 5.0
hole_spacing = 30.0
hole_offset_from_left = 8.0
rib_thickness = 2.0
rib_width = 30.0
rib_height = 6.0

slot_center_x = bracket_length/2 - slot_offset_from_right - slot_width/2
hole_center_x = -bracket_length/2 + hole_offset_from_left
hole_center_y1 = -hole_spacing/2
hole_center_y2 = hole_spacing/2

base = Box(bracket_length, bracket_width, bracket_thickness)
slot_cut = Pos(slot_center_x, 0, 0) * Box(slot_width, slot_height, bracket_thickness)
result = base - slot_cut

vertical_edges = result.edges().filter_by(Axis.Z)
slot_edges = [e for e in vertical_edges if abs(e.center().X - slot_center_x) < slot_width/2 + 1]
result = fillet(slot_edges, fillet_radius)

for y in [hole_center_y1, hole_center_y2]:
    result = result - Pos(hole_center_x, y, 0) * Cylinder(hole_diameter/2, bracket_thickness)

rib = Pos(bracket_length/2 + rib_height/2, 0, 0) * Box(rib_height, rib_width, rib_thickness)
result = result + rib

part = result
part.name = "bracket"
export_step(part, "output.step")