from build123d import *
import math

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
slot_width = 4.0
slot_length = 60.0
slot_depth = wall_thickness * 0.6
chamfer_size = 2.0
mount_hole_dia = 6.0
mount_hole_spacing = 40.0
rib_width = 8.0
rib_height = 12.0
rib_thickness = 3.0
rib_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - slot_box
solid_body = solid_body - Rot(0, 0, 180) * slot_box

for x in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_dia / 2.0, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, rib_width)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_slots_ribs"
export_step(part, "output.step")