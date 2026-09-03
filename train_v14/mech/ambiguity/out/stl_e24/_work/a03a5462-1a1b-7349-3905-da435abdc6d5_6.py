from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 10.0
tab_width = 12.0
tab_height = 8.0
notch_width = 4.0
notch_depth = 6.0

base = Cylinder(outer_diameter / 2, thickness)
tab = Pos(outer_diameter / 2 + tab_width / 2, 0, 0) * Box(tab_width, tab_height, thickness)
solid_body = base + tab

notch = Pos(outer_diameter / 2 + tab_width - notch_width / 2, 0, thickness / 2) * Box(notch_width, notch_depth, thickness)
solid_body = solid_body - notch

hole = Cylinder(inner_diameter / 2, thickness)
solid_body = solid_body - hole

part = solid_body
part.name = "flanged_disc_with_tab"
export_step(part, "output.step")