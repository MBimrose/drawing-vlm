from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 10.0
length = 30.0
collar_length = 12.0
knurl_width = 2.0
knurl_height = 4.0
knurl_count = 12
slot_width = 4.0
slot_length = 15.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
total_length = length + collar_length

solid_body = Cylinder(outer_radius, total_length)
solid_body = solid_body - Cylinder(inner_radius, total_length)

slot = Pos(outer_radius - slot_width/2, 0, total_length/2) * Box(slot_width, slot_width, slot_length)
solid_body = solid_body - slot

for i in range(knurl_count):
    angle = i * 360.0 / knurl_count
    rib = Rot(0, 0, angle) * Pos(outer_radius - knurl_width/2, 0, collar_length/2) * Box(knurl_width, knurl_height, collar_length)
    solid_body = solid_body + rib

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "knurled_shaft_with_slot"
export_step(part, "output.step")