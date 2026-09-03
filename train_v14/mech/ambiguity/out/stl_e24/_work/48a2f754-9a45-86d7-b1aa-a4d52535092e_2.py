from build123d import *

bar_length = 80.0
bar_width = 20.0
bar_height = 12.0
fillet_radius = 2.0
pocket_length = 50.0
pocket_width = 12.0
pocket_depth = 6.0
slot_width = 8.0
slot_length = 30.0
slot_depth = bar_height
hole_diameter = 6.4
hole_spacing_x = 30.0
hole_spacing_y = 10.0
hole_rows = 2
hole_cols = 2

solid = Box(bar_length, bar_width, bar_height)
solid = fillet(solid.edges(), fillet_radius)

pocket = Pos(0, 0, bar_height/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
solid = solid - pocket

slot = Pos(0, bar_width/2 - slot_width/2, 0) * Box(slot_length, slot_width, slot_depth)
solid = solid - slot

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols-1)/2) * hole_spacing_x
        y = (j - (hole_rows-1)/2) * hole_spacing_y
        solid = solid - Pos(x, y, 0) * Cylinder(hole_diameter/2, bar_height * 2)

part = solid
part.name = "bar_with_pocket_slot_holes"
export_step(part, "output.step")