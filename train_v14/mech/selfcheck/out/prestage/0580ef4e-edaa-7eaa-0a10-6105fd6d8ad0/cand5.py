from build123d import *

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
rib_height = 3.0
rib_width = 12.0
rib_count = 6
slot_width = 4.0
slot_length = 60.0
slot_depth = wall_thickness * 0.6
chamfer_size = 2.0
hole_diameter = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius + rib_height / 2.0, 0, 0) * Box(rib_height, rib_width, length)
ribs = rib
for i in range(1, rib_count):
    angle = 360.0 / rib_count * i
    ribs = ribs + Rot(0, 0, angle) * rib

solid_body = solid_body + ribs

slot = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
slots = slot
for i in range(1, 4):
    angle = 360.0 / 4 * i
    slots = slots + Rot(0, 0, angle) * slot

solid_body = solid_body - slots

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

solid_body = solid_body - Cylinder(hole_diameter / 2, length)

part = solid_body
part.name = "hollow_cylinder_with_ribs_slots"
export_step(part, "output.step")