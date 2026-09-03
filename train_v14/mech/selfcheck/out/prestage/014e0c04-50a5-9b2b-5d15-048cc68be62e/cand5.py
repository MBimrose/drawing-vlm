from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 6.0
rib_height = 3.0
rib_width = 6.0
rib_length = bracket_length - 10.0
hole_diameter = 5.0
hole_spacing = 50.0
slot_width = 12.0
slot_depth = 6.0
chamfer_size = 0.5

base = Box(bracket_length, bracket_width, bracket_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, bracket_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
result = base + rib

for x, y in [(-hole_spacing/2, 0), (hole_spacing/2, 0)]:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 20)

slot_box = Pos(0, bracket_width/2 - slot_depth/2, 0) * Box(slot_width, slot_depth, bracket_thickness)
result = result - slot_box

part = result
part.name = "bracket_with_rib"
export_step(part, "output.step")