from build123d import *

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
rib_width = 12.0
rib_thickness = 2.0
rib_count = 6
slot_width = 4.0
slot_length = 30.0
slot_count = 4
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_width, length)
    solid_body = solid_body + rib

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Box(wall_thickness + 0.2, slot_width, slot_length)
    solid_body = solid_body - slot

part = solid_body
part.name = "hollow_cylinder_with_ribs_and_slots"
export_step(part, "output.step")