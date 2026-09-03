from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
length = 60.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 12.0
slot_depth = wall_thickness * 0.9
slot_length = length * 0.6
chamfer_size = 3.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_from_end = 15.0
rib_height = 6.0
rib_width = 30.0
rib_thickness = 4.0
rib_count = 4

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

hole_z = length / 2.0 - hole_offset_from_end
for x in [-hole_spacing / 2.0, hole_spacing / 2.0]:
    solid_body = solid_body - Pos(x, 0, hole_z) * Cylinder(hole_diameter / 2.0, length)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius, 0, 0) * Box(rib_thickness, rib_height, rib_width)
    solid_body = solid_body + rib

part = solid_body
part.name = "hollow_cylinder_with_slot_holes_and_ribs"
export_step(part, "output.step")