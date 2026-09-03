from build123d import *

cover_width = 80.0
cover_height = 60.0
cover_thickness = 5.0
wall_thickness = 3.0
vent_width = 20.0
vent_height = 2.0
vent_offset_y = 15.0
rear_chamfer = 1.0

solid_body = Box(cover_width, cover_height, cover_thickness)

vent_cut = Pos(0, vent_offset_y, cover_thickness / 2) * Box(vent_width, vent_height, cover_thickness)
solid_body = solid_body - vent_cut

rear_face = solid_body.faces().sort_by(Axis.Y)[0]
rear_edges = rear_face.edges()
solid_body = chamfer(rear_edges, rear_chamfer)

part = solid_body
part.name = "cover_with_vent"
export_step(part, "output.step")