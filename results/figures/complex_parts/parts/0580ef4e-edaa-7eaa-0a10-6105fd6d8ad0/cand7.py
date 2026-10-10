from build123d import *

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
rib_width = 4.0
rib_height = 8.0
rib_count = 6
slot_width = 12.0
slot_height = 8.0
slot_depth = 3.0
chamfer_size = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_width/2.0, 0, 0) * Box(rib_width, rib_height, length)
    solid_body = solid_body + rib

slot = Pos(outer_radius - slot_depth/2.0, 0, 0) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot

part = solid_body
part.name = "hollow_cylinder_with_ribs_and_slot"
export_step(part, "output.step")