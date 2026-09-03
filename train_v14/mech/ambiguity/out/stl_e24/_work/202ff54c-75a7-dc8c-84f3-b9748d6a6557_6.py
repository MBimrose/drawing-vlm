from build123d import *

outer_diameter = 80.0
inner_diameter = 40.0
length = 60.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
chamfer_size = 3.0
mount_hole_diameter = 4.0
mount_hole_spacing = 30.0
rib_width = 6.0
rib_height = 12.0
rib_length = length * 0.6
rib_thickness = wall_thickness * 0.6
slot_width = 12.0
slot_length = 20.0
slot_depth = wall_thickness * 0.8

solid_body = Cylinder(outer_diameter / 2.0, length) - Cylinder(inner_diameter / 2.0, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

hole_r = mount_hole_diameter / 2.0
hole_h = length + 10
for x in [outer_diameter / 2.0 - wall_thickness / 2.0, -(outer_diameter / 2.0 - wall_thickness / 2.0)]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_r, hole_h)

rib = Box(rib_thickness, rib_width, rib_length)
rib_pos = Pos(outer_diameter / 2.0 - rib_thickness / 2.0, 0, 0) * rib
ribs = rib_pos
for i in range(1, 4):
    ribs = ribs + Rot(0, 0, i * 90) * rib_pos
solid_body = solid_body + ribs

slot = Box(slot_depth, slot_width, slot_length)
slot_pos = Pos(outer_diameter / 2.0 - slot_depth / 2.0, 0, 0) * slot
solid_body = solid_body - slot_pos

part = solid_body
part.name = "hollow_cylinder_with_ribs_and_slot"
export_step(part, "output.step")