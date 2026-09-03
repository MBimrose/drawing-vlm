from build123d import *
import math

outer_diameter = 60.0
cap_height = 30.0
wall_thickness = 5.0
slot_width = 4.0
slot_height = 10.0
slot_count = 12
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
slot_depth = wall_thickness + 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=cap_height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth/2, 0, cap_height/2) * Box(slot_depth, slot_width, slot_height)
    solid_body = solid_body - slot

part = solid_body
part.name = "cylindrical_cap_with_slots"
export_step(part, "output.step")