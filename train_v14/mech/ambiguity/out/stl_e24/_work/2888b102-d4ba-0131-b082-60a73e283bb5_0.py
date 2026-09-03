from build123d import *

length = 80.0
width = 40.0
thickness = 12.0
wall_thickness = 4.0
tab_length = 20.0
tab_width = 8.0
hole_diameter = 6.0
chamfer_size = 1.0

base = Box(length, width, thickness)
tab = Pos(length/2 + tab_length/2, 0, 0) * Box(tab_length, tab_width, thickness)
solid_body = base + tab

pocket = Box(length - 2*wall_thickness, width - 2*wall_thickness, thickness)
solid_body = solid_body - pocket

hole = Cylinder(hole_diameter/2, thickness)
solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "base_with_tab_pocket_and_hole"
export_step(part, "output.step")