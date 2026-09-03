from build123d import *

outer_radius = 30.0
wall_thickness = 5.0
inner_radius = outer_radius - wall_thickness
body_length = 80.0
boss_radius = 10.0
boss_height = 6.0
boss_offset_z = 15.0
slot_width = 12.0
slot_height = 30.0
slot_depth = 6.0
slot_offset_z = 20.0
chamfer_size = 2.0

result = Pos(0, 0, body_length/2) * Cylinder(outer_radius, body_length)
result = result - Pos(0, 0, body_length/2) * Cylinder(inner_radius, body_length)
result = result + Pos(outer_radius + boss_height/2, 0, boss_offset_z) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
result = result - Pos(outer_radius - slot_depth/2, 0, slot_offset_z) * Box(slot_depth, slot_width, slot_height)
top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_size)

part = result
part.name = "hollow_cylinder_with_boss_and_slot"
export_step(part, "output.step")