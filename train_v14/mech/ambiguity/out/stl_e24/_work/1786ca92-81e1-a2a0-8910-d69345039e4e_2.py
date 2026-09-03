from build123d import *

outer_radius = 20.0
wall_thickness = 3.0
length = 80.0
inlet_diameter = 8.0
outlet_diameter = 8.0
chamfer_size = 1.0
tab_width = 12.0
tab_height = 6.0
tab_thickness = 4.0
tab_offset_z = 20.0

solid_body = Cylinder(outer_radius, length)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

hole_cyl = Cylinder(inlet_diameter / 2, outer_radius * 2 + 2)
solid_body = solid_body - Pos(outer_radius, 0, 0) * Rot(0, 90, 0) * hole_cyl
solid_body = solid_body - Pos(-outer_radius, 0, 0) * Rot(0, 90, 0) * hole_cyl

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

tab = Pos(outer_radius, 0, tab_offset_z - length / 2) * Box(tab_thickness, tab_height, tab_width)
solid_body = solid_body + tab

part = solid_body
part.name = "hollow_cylinder_with_tabs"
export_step(part, "output.step")