from build123d import *

outer_width = 60.0
outer_depth = 40.0
outer_height = 30.0
wall_thickness = 3.0
vent_width = 8.0
vent_height = 20.0
chamfer_size = 0.5

solid = Box(outer_width, outer_depth, outer_height)
top_face = solid.faces().sort_by(Axis.Z)[-1]
bottom_face = solid.faces().sort_by(Axis.Z)[0]
solid = offset(solid, amount=-wall_thickness, openings=[top_face, bottom_face])

vent_box = Box(vent_width, wall_thickness, vent_height)
solid = solid - Pos(0, outer_depth/2 - wall_thickness/2, 0) * vent_box
solid = solid - Pos(0, -outer_depth/2 + wall_thickness/2, 0) * vent_box

vent_box_rot = Box(wall_thickness, vent_width, vent_height)
solid = solid - Pos(outer_width/2 - wall_thickness/2, 0, 0) * vent_box_rot
solid = solid - Pos(-outer_width/2 + wall_thickness/2, 0, 0) * vent_box_rot

vertical_edges = solid.edges().filter_by(Axis.Z)
solid = chamfer(vertical_edges, chamfer_size)

part = solid
part.name = "vented_box"
export_step(part, "output.step")