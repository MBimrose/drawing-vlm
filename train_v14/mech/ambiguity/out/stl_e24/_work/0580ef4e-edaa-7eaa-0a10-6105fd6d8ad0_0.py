from build123d import *
import math

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
rib_height = 12.0
rib_thickness = 3.0
rib_count = 6
slot_width = 4.0
slot_length = 60.0
slot_depth = wall_thickness - 1.0
slot_count = 4
chamfer_size = 2.0
hole_diameter = 12.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius + rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, length)
ribs = rib
for i in range(1, rib_count):
    angle = i * 360.0 / rib_count
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

slot = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
slots = slot
for i in range(1, slot_count):
    angle = i * 360.0 / slot_count
    slots = slots + Rot(0, 0, angle) * slot

solid_body = solid_body - slots

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(hole_diameter / 2, length)

part = solid_body
part.name = "ribbed_tube_with_slots"
export_step(part, "output.step")