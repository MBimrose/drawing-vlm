from build123d import *
import math

outer_diameter = 70.0
wall_thickness = 5.0
length = 80.0
slot_width = 4.0
slot_length = 60.0
slot_depth = wall_thickness / 2.0
chamfer_size = 2.0
rib_width = 8.0
rib_height = 12.0
rib_thickness = 3.0
rib_count = 4
thread_diameter = 12.0
thread_length = 30.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
for i in range(4):
    solid_body = solid_body - Rot(0, 0, i * 90) * slot_box

rib_box = Pos(inner_radius + rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, length - 2 * wall_thickness)
for i in range(rib_count):
    solid_body = solid_body + Rot(0, 0, i * 360 / rib_count) * rib_box

thread_cyl = Pos(0, 0, length / 2.0 - thread_length / 2.0) * Cylinder(thread_diameter / 2.0, thread_length)
solid_body = solid_body - thread_cyl

part = solid_body
part.name = "hollow_cylinder_with_slots_ribs"
export_step(part, "output.step")