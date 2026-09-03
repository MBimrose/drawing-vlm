from build123d import *
import math

outer_diameter = 80.0
hub_diameter = 20.0
thickness = 5.0
slot_width = 5.0
slot_length = 30.0
slot_offset = 10.0
num_slots = 6
chamfer_distance = 0.5
central_hole_diameter = 10.0

outer_radius = outer_diameter / 2.0
hub_radius = hub_diameter / 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
        Circle(hub_radius)
    extrude(amount=thickness)

solid_body = p.part
solid_body = solid_body - Cylinder(central_hole_diameter / 2, thickness * 2)

slot_center_x = hub_radius + slot_offset + slot_length / 2.0
slot_box = Box(slot_length, slot_width, thickness * 2)

for i in range(num_slots):
    angle = i * 360.0 / num_slots
    rotated_slot = Rot(0, 0, angle) * Pos(slot_center_x, 0, 0) * slot_box
    solid_body = solid_body - rotated_slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "slotted_disk"
export_step(part, "output.step")