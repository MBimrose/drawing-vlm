from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 28.0
thickness = 1.5
slot_width = 2.0
slot_length = 5.0
slot_count = 8
chamfer_size = 0.3
rib_width = 10.0
rib_height = 4.0
rib_thickness = 0.5

solid_body = Cylinder(outer_diameter / 2, thickness) - Cylinder(inner_diameter / 2, thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

slot_radius = outer_diameter / 2 - slot_length / 2
for i in range(slot_count):
    angle = math.radians(i * 360.0 / slot_count)
    px = slot_radius * math.cos(angle)
    py = slot_radius * math.sin(angle)
    slot = Pos(px, py, thickness / 2) * Rot(0, 0, math.degrees(angle)) * Box(slot_length, slot_width, thickness)
    solid_body = solid_body - slot

rib = Pos(0, 0, rib_thickness / 2) * Box(rib_width, rib_height, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "washer_with_slots_and_rib"
export_step(part, "output.step")