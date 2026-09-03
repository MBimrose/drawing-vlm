from build123d import *

bracket_length = 60.0
bracket_width = 40.0
bracket_thickness = 8.0
wall_thickness = 2.0
notch_width = 12.0
notch_depth = 6.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 0.5

solid_body = Box(bracket_length, bracket_width, bracket_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

notch_box = Pos(bracket_length/2 - notch_depth/2, 0, 0) * Box(notch_depth, notch_width, bracket_thickness)
solid_body = solid_body - notch_box

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "bracket"
export_step(part, "output.step")