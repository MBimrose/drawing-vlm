from build123d import *
import math

outer_diameter = 60.0
inner_diameter = 50.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2
slot_width = 5.0
slot_depth = wall_thickness + 0.5
num_slots = 12
boss_diameter = 20.0
boss_height = 30.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2
inner_radius = inner_diameter / 2

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

slot_box = Box(slot_depth, slot_width, length)
for i in range(num_slots):
    angle = i * 360.0 / num_slots
    rotated_slot = Rot(0, 0, angle) * Pos(outer_radius + slot_depth / 2, 0, length / 2) * slot_box
    solid_body = solid_body - rotated_slot

boss = Pos(0, 0, -boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
bottom_edges = bottom_face.edges()
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_slots_and_boss"
export_step(part, "output.step")