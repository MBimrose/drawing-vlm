from build123d import *

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
length = 80.0
slot_width = 4.0
slot_depth = 2.0
slot_length = 20.0
boss_radius = 6.0
boss_height = 8.0
hole_diameter = 6.0
chamfer_size = 0.5

result = Cylinder(outer_radius, length) - Cylinder(inner_radius, length)

slot_box = Pos(outer_radius - slot_depth/2, 0, 0) * Box(slot_depth, slot_length, slot_width)
result = result - slot_box

boss_cyl = Pos(outer_radius - boss_height/2, -boss_height/2, 0) * Rot(90, 0, 0) * Cylinder(boss_radius, boss_height)
result = result + boss_cyl

hole_cyl = Pos(outer_radius - boss_height/2, -boss_height/2, 0) * Rot(90, 0, 0) * Cylinder(hole_diameter/2, boss_height)
result = result - hole_cyl

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "hollow_cylinder_with_slot_and_boss"
export_step(part, "output.step")