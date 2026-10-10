from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 4.0
length = 20.0
slot_width = 3.0
slot_count = 4
boss_diameter = 12.0
boss_height = 8.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

solid_body = Rot(0, 90, 0) * Cylinder(outer_radius, length)
solid_body = solid_body - Rot(0, 90, 0) * Cylinder(inner_radius, length)

slot_box = Box(length, slot_width, outer_diameter)
for i in range(slot_count):
    angle = i * 360.0 / slot_count
    rotated_slot = Rot(angle, 0, 0) * slot_box
    solid_body = solid_body - rotated_slot

boss = Pos(length/2 + boss_height/2, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

solid_body = chamfer(solid_body.edges().filter_by(Axis.X), chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_slots_and_boss"
export_step(part, "output.step")