from build123d import *
import math

outer_diameter = 80.0
inner_diameter = 40.0
length = 60.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
slot_width = 12.0
slot_depth = wall_thickness * 0.9
slot_length = 20.0
fillet_radius = 3.0
rib_width = 6.0
rib_height = wall_thickness * 0.8
rib_length = 20.0
rib_count = 4
hole_diameter = 4.0
hole_offset = 15.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
solid_body = solid_body - slot_box

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - rib_height / 2.0, 0, 0) * Box(rib_height, rib_width, rib_length)
    solid_body = solid_body + rib

for x, y in [(hole_offset, 0), (-hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter / 2, length)

part = solid_body
part.name = "hollow_cylinder_with_ribs"
export_step(part, "output.step")