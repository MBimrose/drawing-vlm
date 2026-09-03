from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 30.0
length = 20.0
groove_width = 4.0
groove_depth = 2.0
groove_offset = 5.0
slot_width = 4.0
slot_length = 12.0
slot_count = 4
chamfer_distance = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

solid_body = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

groove = Pos(0, 0, groove_offset + groove_width / 2.0) * Cylinder(inner_radius - groove_depth, groove_width)
solid_body = solid_body - groove

for i in range(slot_count):
    angle = i * 360.0 / slot_count
    slot = Rot(0, 0, angle) * Pos(outer_radius - wall_thickness / 2.0, 0, 0) * Box(wall_thickness, slot_width, slot_length)
    solid_body = solid_body - slot

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_slots"
export_step(part, "output.step")