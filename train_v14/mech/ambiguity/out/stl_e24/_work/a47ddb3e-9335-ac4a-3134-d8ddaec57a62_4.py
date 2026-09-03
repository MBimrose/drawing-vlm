from build123d import *

bracket_length = 60.0
bracket_width = 40.0
bracket_thickness = 5.0
rib_height = 8.0
rib_thickness = 3.0
rib_offset = 20.0
hole_diameter = 5.0
fillet_radius = 0.5
slot_length = 20.0
slot_width = 4.0
slot_offset = 15.0

base = Box(bracket_length, bracket_width, bracket_thickness)
slot = Pos(-bracket_length/2 + slot_offset, bracket_width/2 - slot_offset, 0) * Box(slot_length, slot_width, bracket_thickness)
base = base - slot

rib = Pos(0, bracket_width/2 + rib_thickness/2, 0) * Box(bracket_length - 10, rib_thickness, rib_height)
rib = fillet(rib.edges().filter_by(Axis.Z), fillet_radius)

result = base + rib
result = result - Pos(0, bracket_width/2 + rib_thickness/2, 0) * Cylinder(hole_diameter/2, rib_height)

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")