from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 28.0
thickness = 1.5
slot_width = 2.0
slot_depth = 0.5
slot_count = 12
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
slot_radius = outer_radius - slot_depth / 2.0

solid_body = Cylinder(outer_radius, thickness) - Cylinder(inner_radius, thickness)
solid_body = chamfer(solid_body.edges(), chamfer_size)

for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, 0) * Rot(0, 0, math.degrees(angle)) * Box(slot_width, slot_depth, thickness)
    solid_body = solid_body - slot

part = solid_body
part.name = "ring_with_slots"
export_step(part, "output.step")