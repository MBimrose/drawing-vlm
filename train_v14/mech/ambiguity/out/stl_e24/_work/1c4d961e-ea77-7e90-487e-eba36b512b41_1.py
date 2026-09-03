from build123d import *

outer_size = 80.0
height = 40.0
wall_thickness = 5.0
rib_thickness = 3.0
rib_height = 5.0
hole_diameter = 12.0
chamfer_size = 2.0

base = Box(outer_size, outer_size, height)
top_face = base.faces().sort_by(Axis.Z)[-1]
shell_body = offset(base, amount=-wall_thickness, openings=[top_face])

vertical_edges = shell_body.edges().filter_by(Axis.Z)
shell_body = chamfer(vertical_edges, chamfer_size)

rib1 = Pos(0, 0, height/2 - rib_height/2) * Box(outer_size - 2*wall_thickness, rib_thickness, rib_height)
rib2 = Pos(0, 0, height/2 - rib_height/2) * Box(rib_thickness, outer_size - 2*wall_thickness, rib_height)
shell_body = shell_body + rib1 + rib2

hole_tool = Rot(0, 90, 0) * Cylinder(hole_diameter/2, outer_size + 10)
shell_body = shell_body - Pos(-outer_size/2, 0, 0) * hole_tool
shell_body = shell_body - Pos(outer_size/2, 0, 0) * hole_tool

part = shell_body
part.name = "shelled_box_with_ribs_and_holes"
export_step(part, "output.step")