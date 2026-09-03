from build123d import *

outer_diameter = 60.0
height = 30.0
wall_thickness = 5.0
groove_depth = 2.0
groove_width = 4.0
groove_position = 20.0
vent_slot_width = 4.0
vent_slot_height = 10.0
vent_slot_count = 12
chamfer_distance = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
groove_radius = inner_radius - groove_depth

solid_body = Cylinder(outer_radius, height)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove = Pos(0, 0, groove_position) * Cylinder(groove_radius, groove_width)
solid_body = solid_body - groove

import math
slot_radius = outer_radius - wall_thickness / 2.0
for i in range(vent_slot_count):
    angle = math.radians(i * 360.0 / vent_slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, 0) * Box(wall_thickness + 0.2, vent_slot_width, vent_slot_height)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

part = solid_body
part.name = "vented_cup"
export_step(part, "output.step")