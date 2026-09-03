from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 30.0
thickness = 5.0
hub_diameter = 12.0
hub_height = 3.0
vent_slot_width = 4.0
vent_slot_length = (outer_diameter - inner_diameter) / 2 - 5.0
num_vent_slots = 6
chamfer_size = 0.5
relief_slot_width = 2.0
relief_slot_length = 8.0
relief_depth = 1.0
num_relief_slots = 4

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
        Circle(inner_diameter / 2, mode=Mode.SUBTRACT)
    extrude(amount=thickness)

solid_body = p.part
hub = Pos(0, 0, hub_height / 2) * Cylinder(hub_diameter / 2, hub_height)
solid_body = solid_body + hub

for i in range(num_vent_slots):
    angle_deg = i * 360.0 / num_vent_slots
    slot = Rot(0, 0, angle_deg) * Pos(inner_diameter / 2 + vent_slot_length / 2, 0, thickness / 2) * Box(vent_slot_length, vent_slot_width, thickness)
    solid_body = solid_body - slot

for i in range(num_relief_slots):
    angle_deg = i * 360.0 / num_relief_slots
    slot = Rot(0, 0, angle_deg) * Pos(hub_diameter / 2 + relief_slot_length / 2, 0, thickness - relief_depth / 2) * Box(relief_slot_length, relief_slot_width, relief_depth)
    solid_body = solid_body - slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "ventilated_disc"
export_step(part, "output.step")