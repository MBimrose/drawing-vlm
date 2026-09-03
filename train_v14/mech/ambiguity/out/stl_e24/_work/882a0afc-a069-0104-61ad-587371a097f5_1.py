from build123d import *
import math

outer_radius = 30.0
wall_thickness = 5.0
cap_height = 30.0
vent_slot_width = 4.0
vent_slot_height = 10.0
vent_count = 12
chamfer_size = 2.0

solid_body = Cylinder(outer_radius, cap_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-2:]
solid_body = chamfer(top_edges, chamfer_size)

slot_radius = outer_radius - wall_thickness / 2
for i in range(vent_count):
    angle = math.radians(i * 360.0 / vent_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, 0) * Box(wall_thickness + 0.2, vent_slot_width, vent_slot_height)
    solid_body = solid_body - slot

part = solid_body
part.name = "vented_cap"
export_step(part, "output.step")