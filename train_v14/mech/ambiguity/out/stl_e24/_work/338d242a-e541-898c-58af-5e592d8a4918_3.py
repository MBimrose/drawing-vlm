from build123d import *

arm_length = 80.0
outer_radius = 12.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
slot_width = 4.0
slot_length = 20.0
hole_diameter = 2.0
hole_spacing = 6.0
hole_count = 10
hole_start_offset = 12.0

solid_body = Cylinder(outer_radius, arm_length) - Cylinder(inner_radius, arm_length)

slot_cut = Pos(outer_radius - wall_thickness / 2, 0, -arm_length / 2 + slot_length / 2) * Box(wall_thickness + 0.2, slot_width, slot_length)
solid_body = solid_body - slot_cut

for i in range(hole_count):
    z_pos = -arm_length / 2 + hole_start_offset + i * hole_spacing
    hole = Pos(outer_radius - wall_thickness / 2, 0, z_pos) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, wall_thickness + 0.2)
    solid_body = solid_body - hole

part = solid_body
part.name = "hollow_cylinder_with_slot_and_holes"
export_step(part, "output.step")