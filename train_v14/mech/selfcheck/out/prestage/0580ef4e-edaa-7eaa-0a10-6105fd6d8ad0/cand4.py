from build123d import *
import math

outer_radius = 35.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
length = 80.0
chamfer_size = 2.0
rib_count = 6
rib_thickness = 2.0
rib_height = 12.0
slot_width = 4.0
slot_length = 0.7 * length
slot_depth = wall_thickness - 0.5
hole_diameter = 5.0
hole_radius = hole_diameter / 2.0
hole_count = 4

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness / 2.0, 0, 0) * Box(rib_thickness, rib_height, length)
    solid_body = solid_body + rib

for i in range(4):
    angle = i * 360.0 / 4
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth / 2.0, 0, 0) * Box(slot_depth, slot_width, slot_length)
    solid_body = solid_body - slot

for i in range(hole_count):
    angle = i * 360.0 / hole_count
    hole = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Cylinder(hole_radius, wall_thickness + 0.2)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_ribs_slots_holes"
export_step(part, "output.step")