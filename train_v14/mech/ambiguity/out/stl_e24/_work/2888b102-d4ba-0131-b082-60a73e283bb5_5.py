from build123d import *

overall_length = 80.0
overall_width = 40.0
overall_thickness = 12.0
wall_thickness = 4.0
latch_tab_length = 20.0
latch_tab_width = 8.0
relief_groove_width = 6.0
relief_groove_depth = 2.0
hole_diameter = 4.0
hole_spacing = 30.0
chamfer_distance = 1.0

base = Box(overall_length, overall_width, overall_thickness)
tab = Pos(overall_length/2 + latch_tab_length/2, 0, 0) * Box(latch_tab_length, latch_tab_width, overall_thickness)
solid_body = base + tab

inner_cut = Box(overall_length - 2*wall_thickness, overall_width - 2*wall_thickness, overall_thickness)
solid_body = solid_body - inner_cut

groove = Pos(0, 0, overall_thickness - relief_groove_depth/2) * Box(overall_length - 2*wall_thickness, relief_groove_width, relief_groove_depth)
solid_body = solid_body - groove

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, overall_thickness)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "latch_plate"
export_step(part, "output.step")