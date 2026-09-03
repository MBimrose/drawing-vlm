from build123d import *

panel_width = 80.0
panel_height = 50.0
panel_thickness = 6.0
hole_diameter = 6.0
hole_spacing = 10.0
hole_count = 7
edge_chamfer = 0.8
slot_length = 30.0
slot_width = 6.0
slot_offset_y = -12.0
rib_width = 12.0
rib_height = 8.0
rib_thickness = 2.0
rib_offset_x = -30.0

solid_body = Box(panel_width, panel_height, panel_thickness)

top_y_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_y_face.edges(), edge_chamfer)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, panel_thickness / 2) * Cylinder(hole_diameter / 2, panel_thickness + 2)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=panel_thickness + 2)
slot_solid = slot_bp.part
solid_body = solid_body - Pos(-slot_length / 2, slot_offset_y, 0) * slot_solid

rib_solid = Pos(rib_offset_x, 0, -rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib_solid

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, 1.0)

part = solid_body
part.name = "panel_with_holes_slot_and_rib"
export_step(part, "output.step")