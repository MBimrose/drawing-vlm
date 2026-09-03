from build123d import *

arm_length = 80.0
arm_width = 20.0
arm_thickness = 10.0
fillet_radius = 3.0
chamfer_distance = 0.5
slot_width = 6.0
slot_length = 10.0
slot_offset = 20.0
hole_diameter = 5.0
hole_spacing = 12.0
hole_offset = 10.0
boss_radius = 3.0
boss_length = 12.0
boss_offset = 30.0

solid_body = Box(arm_width, arm_length, arm_thickness)

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, fillet_radius)

slot = Pos(0, slot_offset - arm_length/2, 0) * Box(slot_width, slot_length, arm_thickness)
solid_body = solid_body - slot

for x in [-hole_spacing/2, hole_spacing/2]:
    hole = Pos(x, hole_offset - arm_length/2, 0) * Cylinder(hole_diameter/2, arm_thickness)
    solid_body = solid_body - hole

boss = Pos(boss_length/2, boss_offset - arm_length/2, arm_thickness + boss_radius) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_length)
solid_body = solid_body + boss

vert_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vert_edges, chamfer_distance)

part = solid_body
part.name = "arm_with_slot_holes_boss"
export_step(part, "output.step")