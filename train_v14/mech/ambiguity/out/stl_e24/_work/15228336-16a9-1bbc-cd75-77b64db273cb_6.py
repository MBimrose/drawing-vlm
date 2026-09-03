from build123d import *

base_width = 70.0
base_depth = 20.0
base_height = 10.0
tab_length = 30.0
tab_width = 6.0
hole_diameter = 4.0
hole_spacing = 15.0
hole_count = 4
pocket_width = 4.0
pocket_depth = 3.0
pocket_offset = 10.0

base = Pos(0, 0, base_height/2) * Box(base_width, base_depth, base_height)
tab = Pos(base_width/2 - tab_width/2, base_depth/2 + tab_width/2, base_height) * Box(tab_length, tab_width, base_height)
result = base + tab

pocket = Pos(pocket_offset, base_depth/2 + tab_width - pocket_depth/2, base_height) * Box(pocket_width, pocket_depth, pocket_width)
result = result - pocket

for i in range(hole_count):
    x = base_width/2 - tab_width/2 + i * hole_spacing
    y = base_depth/2 + tab_width/2
    hole = Pos(x, y, base_height) * Cylinder(hole_diameter/2, base_height)
    result = result - hole

part = result
part.name = "base_with_tab_pocket_and_holes"
export_step(part, "output.step")