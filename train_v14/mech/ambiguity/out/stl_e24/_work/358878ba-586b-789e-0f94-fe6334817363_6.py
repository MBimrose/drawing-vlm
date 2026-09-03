from build123d import *

outer_width = 80.0
outer_depth = 30.0
outer_height = 40.0
wall_thickness = 2.0
channel_width = 20.0
channel_depth = 10.0
chamfer_size = 0.5
hole_diameter = 6.0

solid_body = Box(outer_width, outer_depth, outer_height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

channel_box = Pos(0, 0, outer_height/2 - channel_depth/2) * Box(channel_width, outer_depth, channel_depth)
solid_body = solid_body - channel_box

front_face = solid_body.faces().sort_by(Axis.Y)[-1]
front_edges = front_face.edges()
solid_body = chamfer(front_edges, chamfer_size)

hole_cyl = Pos(0, 0, outer_height/2 - channel_depth/2) * Cylinder(hole_diameter/2, outer_depth)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "hollow_box_with_channel"
export_step(part, "output.step")