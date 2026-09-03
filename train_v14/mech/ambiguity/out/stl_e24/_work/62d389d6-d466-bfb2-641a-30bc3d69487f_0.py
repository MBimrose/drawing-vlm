from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
tab_length = 30.0
tab_width = 12.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
pocket_chamfer = 0.5
hole_diameter = 5.0
hole_spacing = 30.0
slot_width = 6.0
slot_length = 30.0
slot_spacing = 20.0

base = Box(bracket_length, bracket_width, bracket_thickness)
tab = Pos(0, bracket_width/2 + tab_width/2, 0) * Box(tab_length, tab_width, bracket_thickness)
result = base + tab

pocket = Pos(0, 0, bracket_thickness - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
pocket = chamfer(pocket.edges().filter_by(Axis.Z), pocket_chamfer)
result = result - pocket

for x in [-hole_spacing/2, hole_spacing/2]:
    result = result - Pos(x, 0, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 100)

for x in [-slot_spacing/2, slot_spacing/2]:
    result = result - Pos(x, 0, bracket_thickness/2) * Box(slot_width, slot_length, bracket_thickness)

part = result
part.name = "bracket"
export_step(part, "output.step")