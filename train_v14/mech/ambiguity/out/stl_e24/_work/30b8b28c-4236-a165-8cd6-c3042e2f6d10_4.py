from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 28.0
thickness = 1.5
chamfer_size = 0.3
slot_width = 2.0
slot_depth = 1.5
num_slots = 6
slot_radius = outer_diameter/2 - slot_width/2 - 2.0

solid_body = Cylinder(outer_diameter/2, thickness) - Cylinder(inner_diameter/2, thickness)
solid_body = chamfer(solid_body.edges(), chamfer_size)

for i in range(num_slots):
    angle = math.radians(i * 360.0 / num_slots)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, 0) * Rot(0, 0, math.degrees(angle)) * Box(slot_width, slot_depth, thickness)
    solid_body = solid_body - slot

part = solid_body
part.name = "ring_with_slots"
export_step(part, "output.step")