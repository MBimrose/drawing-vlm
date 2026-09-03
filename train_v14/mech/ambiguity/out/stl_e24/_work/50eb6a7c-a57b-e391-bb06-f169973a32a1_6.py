from build123d import *

spacer_width = 70.0
spacer_depth = 40.0
spacer_height = 12.0
rear_fillet_radius = 4.0
slot_width = 10.0
slot_height = 8.0
slot_depth = 8.0
hole_diameter = 6.0
hole_depth = 8.0
hole_spacing = spacer_width / 4.0
chamfer_distance = 0.8
rib_width = 12.0
rib_depth = 6.0
rib_height = 4.0
rib_offset_x = -spacer_width/2 + rib_width/2 + 5.0

solid_body = Box(spacer_width, spacer_depth, spacer_height)

rear_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Y)[-2:]
solid_body = fillet(rear_edges, rear_fillet_radius)

slot_box = Pos(spacer_width/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot_box

for x in [-hole_spacing, 0, hole_spacing]:
    hole = Pos(x, 0, spacer_height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    solid_body = solid_body - hole

rib = Pos(rib_offset_x, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + rib

bottom_edges = solid_body.edges().filter_by(Axis.X).sort_by(Axis.Z)[:2]
solid_body = chamfer(bottom_edges, chamfer_distance)

part = solid_body
part.name = "spacer_with_slot_holes_rib"
export_step(part, "output.step")