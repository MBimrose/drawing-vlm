from build123d import *
import math

outer_radius = 35.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
height = 80.0
chamfer_size = 2.0
central_bore_diameter = 12.0
slot_width = 4.0
slot_length = height * 0.7
slot_depth = wall_thickness - 0.5
slot_count = 8
rib_width = 6.0
rib_height = 12.0
rib_thickness = 3.0
rib_count = 6

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)
solid_body = solid_body - Cylinder(central_bore_diameter / 2, height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(slot_count):
    angle_deg = i * 360.0 / slot_count
    slot = Rot(0, 0, angle_deg) * Pos(outer_radius - slot_depth / 2, 0, 0) * Box(slot_depth, slot_width, slot_length)
    solid_body = solid_body - slot

for i in range(rib_count):
    angle_deg = i * 360.0 / rib_count
    rib = Rot(0, 0, angle_deg) * Pos(inner_radius - rib_thickness / 2, 0, 0) * Box(rib_thickness, rib_height, rib_width)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_slots_and_ribs"
export_step(part, "output.step")