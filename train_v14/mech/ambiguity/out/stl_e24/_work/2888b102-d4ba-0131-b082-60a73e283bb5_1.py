from build123d import *

outer_width = 80.0
outer_height = 40.0
thickness = 12.0
wall_thickness = 4.0
tab_width = 20.0
tab_height = 8.0
central_hole_diameter = 5.0
chamfer_distance = 1.0

base = Box(outer_width, outer_height, thickness)
tab = Pos(outer_width/2 + tab_width/2, 0, 0) * Box(tab_width, tab_height, thickness)
solid_body = base + tab

inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - 2 * wall_thickness
cavity = Box(inner_width, inner_height, thickness)
solid_body = solid_body - cavity

solid_body = solid_body - Cylinder(central_hole_diameter/2, thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "frame_with_tab"
export_step(part, "output.step")