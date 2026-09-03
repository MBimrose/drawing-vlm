from build123d import *

base_length = 70.0
base_width = 20.0
base_thickness = 10.0
tab_length = 40.0
tab_width = 6.0
slot_length = 30.0
slot_width = 6.0
hole_diameter = 4.0
hole_spacing = 20.0
chamfer_distance = 1.0
notch_width = 4.0
notch_depth = 3.0

base = Box(base_length, base_width, base_thickness)
tab = Pos(base_length/2 - tab_length/2, base_width/2 + tab_width/2, base_thickness/2) * Box(tab_length, tab_width, base_thickness)
result = base + tab

slot = Pos(base_length/2 - tab_length/2, base_width/2 + tab_width/2, base_thickness/2) * Box(slot_length, slot_width, base_thickness)
result = result - slot

for x, y in [(hole_spacing/2, 0), (base_length - hole_spacing/2, 0)]:
    result = result - Pos(x, y, base_thickness/2) * Cylinder(hole_diameter/2, base_thickness)

notch = Pos(base_length/2 - tab_length/2, base_width/2 + tab_width - notch_depth/2, base_thickness/2) * Box(notch_width, notch_depth, base_thickness)
result = result - notch

part = result
part.name = "base_with_tab"
export_step(part, "output.step")