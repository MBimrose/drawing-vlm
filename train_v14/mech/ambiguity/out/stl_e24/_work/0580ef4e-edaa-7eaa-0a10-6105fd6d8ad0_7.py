from build123d import *

outer_diameter = 70.0
length = 80.0
wall_thickness = 5.0
rib_width = 10.0
rib_height = 12.0
rib_count = 6
slot_width = 4.0
slot_length = 60.0
slot_count = 6
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

rib = Pos(inner_radius, 0, 0) * Box(rib_width, rib_height, wall_thickness)
for i in range(rib_count):
    angle = i * 360.0 / rib_count
    solid_body = solid_body + Rot(0, 0, angle) * rib

slot = Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Box(slot_width, wall_thickness, slot_length)
for i in range(slot_count):
    angle = i * 360.0 / slot_count
    solid_body = solid_body - Rot(0, 0, angle) * slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "ribbed_cylinder_with_slots"
export_step(part, "output.step")