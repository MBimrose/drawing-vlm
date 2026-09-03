from build123d import *

outer_width = 60.0
outer_height = 40.0
outer_depth = 8.0
wall_thickness = 2.0
notch_width = 12.0
notch_height = 15.0
hole_diameter = 5.0
hole_spacing = 30.0
chamfer_size = 0.5

solid_body = Box(outer_width, outer_height, outer_depth)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

notch = Pos(outer_width/2 - wall_thickness/2, 0, 0) * Box(wall_thickness, notch_width, notch_height)
solid_body = solid_body - notch

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, outer_depth * 2)

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "shelled_box_with_notch_and_holes"
export_step(part, "output.step")