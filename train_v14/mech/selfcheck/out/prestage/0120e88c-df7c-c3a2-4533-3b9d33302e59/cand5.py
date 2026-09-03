from build123d import *

panel_width = 80.0
panel_height = 60.0
panel_thickness = 5.0
chamfer_distance = 1.0
slot_width = 20.0
slot_height = 2.0
slot_offset_y = panel_height/2 - 10.0

solid_body = Box(panel_width, panel_height, panel_thickness)

# Chamfer edges on the <Y face
y_face = solid_body.faces().sort_by(Axis.Y)[0]
y_edges = y_face.edges()
solid_body = chamfer(y_edges, chamfer_distance)

# Cut slot from top face
slot = Pos(0, slot_offset_y, panel_thickness/4) * Box(slot_width, slot_height, panel_thickness/2)
solid_body = solid_body - slot

part = solid_body
part.name = "panel_with_chamfer_and_slot"
export_step(part, "output.step")