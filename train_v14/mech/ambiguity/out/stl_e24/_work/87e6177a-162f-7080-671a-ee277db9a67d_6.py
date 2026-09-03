from build123d import *
import math

outer_diameter = 80.0
length = 60.0
wall_thickness = 5.0
groove_width = 2.0
groove_depth = 2.0
slot_width = 2.0
slot_depth = 10.0
slot_count = 6
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

groove = Pos(outer_radius - groove_depth/2.0, 0, -length/2.0 + groove_depth/2.0) * Box(groove_width, length, groove_depth)
solid_body = solid_body - groove

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - slot_depth/2.0, 0, -length/2.0 + slot_depth/2.0) * Box(slot_width, wall_thickness, slot_depth)
    solid_body = solid_body - slot

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_slots"
export_step(part, "output.step")