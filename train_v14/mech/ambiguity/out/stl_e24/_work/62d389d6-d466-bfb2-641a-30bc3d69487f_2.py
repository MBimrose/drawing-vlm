from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 8.0
tab_length = 30.0
tab_width = 12.0
slot_width = 6.0
slot_length = 30.0
slot_spacing = 20.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 1.0

base = Box(bracket_length, bracket_width, bracket_thickness)
tab = Pos(0, bracket_width/2 + tab_width/2, 0) * Box(tab_length, tab_width, bracket_thickness)
result = base + tab

slot1 = Pos(-slot_spacing/2, 0, bracket_thickness/2) * Box(slot_width, slot_length, bracket_thickness)
slot2 = Pos(slot_spacing/2, 0, bracket_thickness/2) * Box(slot_width, slot_length, bracket_thickness)
result = result - slot1 - slot2

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, bracket_width/2 + tab_width/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, 100)
    result = result - hole

part = result
part.name = "bracket_with_tab_slots_holes"
export_step(part, "output.step")