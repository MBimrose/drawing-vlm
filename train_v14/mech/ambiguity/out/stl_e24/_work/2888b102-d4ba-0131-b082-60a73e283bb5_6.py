from build123d import *

outer_width = 80.0
outer_depth = 40.0
outer_height = 12.0
wall_thickness = 4.0
tab_width = 20.0
tab_height = 8.0
chamfer_size = 1.0
hole_diameter = 4.0

base = Box(outer_width, outer_depth, outer_height)
tab = Pos(outer_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, outer_height)
solid_body = base + tab

pocket = Box(outer_width - 2*wall_thickness, outer_depth - 2*wall_thickness, outer_height)
solid_body = solid_body - pocket

hole = Cylinder(hole_diameter/2, outer_height)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "XMountSocket"
export_step(part, "output.step")